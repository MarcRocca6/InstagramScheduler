# /usr/bin/env python
import json
import time
import nltk
import pprint
import datetime
import random
import operator
import itertools 
import contextlib
import pandas as pd 
from .login_data import *
from random import randint
from time import sleep
from InstagramAPI import InstagramAPI
from geopy.geocoders import Nominatim

# Scouting Login
login_sentry = ['*****', "*****"]


class InstaBot:

	def __init__(self, name):
		global Time
		Time = time.time()
		if name == "Sentry":
			username = login_sentry[0]
			password = login_sentry[1]
		elif name == "Bar":
			username = login['username']
			password = login['password']
		elif name == "Fake":
			username = login_sentry[0]
			password = login_sentry[1]
		self.api = InstagramAPI(username, password)
		with contextlib.redirect_stdout(None):
			self.api.login()
		m,s = divmod((time.time()-Time), 60)

	def __del__(self):
		self.api.logout()

	# ---------------------------------------------------------- 
	# -------------------  Get Functions  ---------------------- 
	# ---------------------------------------------------------- 

	# Returns list of people who follow you
	def get_followers(self):
		self.api.getSelfUserFollowers() # Get your followers
		result = self.api.LastJson
		follower_list = []
		for user in result['users']:
			follower_list.append({'pk':user['pk'], 'username':user['username']})
		return follower_list

	# Returns list of people you follow
	def get_followingUsers(self):
	    self.api.getSelfUsersFollowing() # Get users you are following
	    result = self.api.LastJson
	    following_users = []
	    for user in result['users']:
	    	following_users.append({'pk':user['pk'],'username':user['username']})
	    return following_users

	# Returns users post feed
	def get_userFeed(self, userID):
	    user_posts = self.api.getUserFeed(userID) # Get user feed
	    return self.api.LastJson

	# Pass in username and returns userID
	# Returns False if a user does not exist
	def get_userID(self, username):
		try:
			self.api.searchUsername(username)
			result = self.api.LastJson
			return result['user']['pk']
		except:
			return False

	# Returns user infromation
	def get_userInfo(self, id):
			self.api.getUsernameInfo(id)
			return self.api.LastJson		

	# Returns list of user name and id
	def get_userList(self, username_list):
		data = []
		for x in username_list:
			user = {}
			user['pk'] = self.get_userID(x)
			user['username'] = x
			if user['pk'] != False:
				data.append(user)
		return data

	# Returns list of all self notifications
	def get_notifcations(self):
		activity = []    
		self.api.getRecentActivity()
		recent_activity_response = self.api.LastJson 
		for notifcation in recent_activity_response['old_stories']:
		    activity.append(notifcation['args']['text'])
		return activity

	# Returns list of people who liked the last post of a certain user
	def get_likesList(self, username):
		users_list = []
		self.api.searchUsername(username)
		result = self.api.LastJson
		username_id = result['user']['pk'] # Get user ID
		user_posts = self.api.getUserFeed(username_id) # Get user feed
		result = self.api.LastJson
		media_id = result['items'][0]['id'] # Get 2nd most recent post
		self.api.getMediaLikers(media_id) # Get users who liked
		users = self.api.LastJson['users']
		for user in users: # Push users to list
			users_list.append({'pk':user['pk'], 'username':user['username']})
		return users_list

	# Returns basic self information
	def get_profileInfo(self):
	    self.api.getSelfUsernameInfo()
	    result = self.api.LastJson
	    username = result['user']['username']
	    full_name = result['user']['full_name']
	    profile_pic_url = result['user']['profile_pic_url']
	    followers = result['user']['follower_count']
	    following = result['user']['following_count']
	    media_count = result['user']['media_count']
	    df_profile = {
			    	'username':username,
			    	'full name': full_name,
			    	'followers':followers,
			    	'following':following
	        		}
	    return df_profile

	# Returns list of all pictures in your feed
	def get_feedUrls(self):
	    image_urls = []
	    self.api.getSelfUserFeed()
	    result = self.api.LastJson
	    # formatted_json_str = pprint.pformat(result)
	    # print(formatted_json_str)
	    if 'items' in result.keys():
	        for item in result['items'][0:5]:
	            if 'image_versions2' in item.keys():
	                image_url = item['image_versions2']['candidates'][1]['url']
	                image_urls.append(image_url)
	    return image_urls

	# ---------------------------------------------------------- 
	# -----------------  Follow Functions  --------------------- 
	# ---------------------------------------------------------- 

	# Follow list of users
	def follow_users(self, users_list):
		following_users = self.get_followingUsers()
		for user in users_list:
			self.api.login()
			global followsToday
			global followLimit
			if followsToday > followLimit: 
				print('Max Users Followed Today: ', followsToday)
				return False
			user = random.choice(users_list)
			if not user in following_users: # if new user is not in your following users                   
				print('Following @' + user['username'])
				self.api.follow(user['pk'])
				followsToday = followsToday + 1
				f = open('Instagram/Data/follow.txt', 'a')
				f.write(user['username'])
				f.close()
				sleep(randint(60,400))
			else:
				print('Already following @' + user['username'])
				sleep(randint(15,50))

	# Unfollows list of users
	def unfollow_users(self, users_list):
		for user in users_list:
			self.api.login()
			global unfollowsToday
			global unfollowsToday
			unfollowsToday = unfollowsToday + 1
			if unfollowsToday > unfollowLimit: 
				print('Max Users Unfollowed Today: ', unfollowsToday)
				return False
			user = random.choice(users_list)
			print('Unfollowing @' + user['username'])
			self.api.unfollow(user['pk'])
			f = open('Instagram/Data/unfollow.txt', 'a')
			f.write(user['username'])
			f.close()
			# set this really long to avoid from suspension
			sleep(randint(60,400))

	# Unfollows people who you follow but who dont follow back
	def unfollow_unfollowers(self):
	    not_followers = []
	    follower_users = self.get_followers()
	    following_users = self.get_followingUsers() 
	    for user in following_users:
	    	if not user in follower_users: # if the user not follows you
	    		not_followers.append(user)
	    self.unfollow_users(not_followers)

	# Pass in list of usernames and returns list of usernames
	# of people that you are not following
	def check_following(self, users_list):
		following_users = self.get_followingUsers()
		not_following = following_users
		for following in following_users:
			for user in users_list:
				if following['username'] == user:
					not_following.remove(user)
		return not_following

	# Follows every user that comes up in the notifications
	# if we are not already following them
	def follow_notifications(self):
		users = []
		notifications = self.get_notifcations()
		for string in notifications:
			words = string.split()
			for name in words:
				# If its not a word
				if not self.check_word(name):
					# If its a valid user
					userID = self.get_userID(name)
					if not userID == False:
						users.append({'username' : name, 'pk' : userID}) 
		self.follow_users(users)

	# ---------------------------------------------------------- 
	# -------------------  Feed Functions  --------------------- 
	# ---------------------------------------------------------- 

	# Returns all locations that have the keyword
	def search_locations(self, location):
		locations = []
		self.api.searchLocation(location)
		result = self.api.LastJson
		for x in result['items']:
			place = x['location']
			locations.append({'name' : place['name'], 'pk' : place['pk']})		
		return locations

	# Returns all tags that have the keyword
	# and over a certain number of posts
	def search_tags(self, tag, num):
		tags = []
		media = []
		self.api.searchTags(tag)
		result = self.api.LastJson
		for x in result['results']:
			if x['media_count'] < 10000: continue 
			tags.append(x['name'])
			media.append(x['media_count'])	
		# Combine 2 lists together to form dic
		res = {tags[i]: media[i] for i in range(len(tags))} 
		# Sort dictionary upon the values descending
		sort = dict(sorted(res.items(), key=operator.itemgetter(1), reverse=True))
		return dict(list(sort.items())[0: num]).keys()  	

	# Returns the feed for a location
	def location_feed(self, locationID):
		self.api.getLocationFeed(locationID, maxid='99999')
		result = self.api.LastJson
		return result

	# Returns the popular feed
	def popular_feed(self):
		self.api.getPopularFeed()
		result = self.api.LastJson
		return result

	# Returns the feed for a hashtag
	def hashtag_feed(self, hashtag):
		self.api.getHashtagFeed(hashtag)
		result = self.api.LastJson
		return result

	# Returns the feed of a users photos
	def user_feed(self, userID):
		self.api.getUserFeed(userID, maxid='99999')
		result = self.api.LastJson
		return result

	# Returns information of a feeds posts
	def feed_info(self, feed, min_followers):
		feed_info = []
		for x in feed['items']:
			if min_followers > 0:
				self.api.getUsernameInfo(x['user']['pk'])
				result = self.api.LastJson
				followers = result['user']['follower_count']
				if followers < min_followers: continue
			time_ = datetime.datetime.fromtimestamp(x['taken_at']).strftime('%Y-%m-%d %H:%M:%S')
			# time_ =  round((time.time() - x['taken_at'])/60,2)
			post = 	{
					'name' : x['user']['username'] ,
					'pk' : x['user']['pk'],
					'#likes' : x['like_count'],
					'time' : time_,
					'hashtag' : [],
					'tag' : []
					}
			if min_followers > 0:
				post['#followers'] = followers
			if 'comment_count' in x.keys():
				num_comments = x['comment_count']
				post['#comments'] = num_comments
			if not x['caption'] is None:
				hashtag, tag = self.extract_tags(x['caption']['text'])
				post['hashtag'] = hashtag
				post['tag'] = tag
			if 'preview_comments' in x.keys():
				if x['preview_comments'] != []:
					for comment in x['preview_comments']:
						hashtag, tag = self.extract_tags(comment['text'])
						# Add to post dict. Check if there have been entries already
						post['hashtag'].extend(hashtag)
						post['tag'].extend(tag)
			feed_info.append(post)
		return feed_info

	# Returns information of a feeds posts following info
	# Same as feed_info except no hashtags
	def post_followInfo(self, feed, min_followers):
		feed_info = []
		for x in feed['items']:
			if min_followers > 0:
				self.api.getUsernameInfo(x['user']['pk'])
				result = self.api.LastJson
				followers = result['user']['follower_count']
				if followers < min_followers: continue
			post = 	{
					'name' : x['user']['username'] ,
					'pk' : x['user']['pk'],
					'#likes' : x['like_count'],

					}
			if min_followers > 0:
				post['#followers'] = followers
			feed_info.append(post)
		return feed_info

	# ---------------------------------------------------------- 
	# ------------------  Comment Functions  ------------------- 
	# ---------------------------------------------------------- 

	# Like the last 3 posts from the username 
	def like_userPost(self, username_id):
		try:
		    # self.api.searchUsername(username)
		    # result = self.api.LastJson
		    # username_id = result['user']['pk'] # Get user ID
		    user_posts = self.api.getUserFeed(username_id) # Get user feed
		    result = self.api.LastJson
		    media_id = result['items'][0]['id'] # Get 2nd most recent post
		    media_id2 = result['items'][1]['id']
		    media_id3 = result['items'][2]['id']
		    self.api.like(media_id)
		    self.api.like(media_id2)
		    self.api.like(media_id3)
		    return True 
		except: return False 

	# Comment on last post from a user
	def comment_userPost(self, text, username):
		try:
			self.api.searchUsername(username)
			result = self.api.LastJson
			username_id = result['user']['pk'] # Get user ID
			user_posts = self.api.getUserFeed(username_id) # Get user feed
			result = self.api.LastJson
			media_id = result['items'][0]['id'] # Get 2nd most recent post
			self.api.like(media_id)
			self.api.comment(media_id, text)
			return True 
		except: 
			print('Error')
			return False 

	def uploadPhoto(self, path, caption):
		self.api.uploadPhoto(path, caption=caption)
			# 

	# ---------------------------------------------------------- 
	# ------------------  Helper Functions  -------------------- 
	# ---------------------------------------------------------- 

	# Logs out from the account
	def logout(self):
		with contextlib.redirect_stdout(None): 
			self.api.logout()

	# Check if a string is a valid english word
	def check_word(self, username):
		english_vocab = set(w.lower() for w in nltk.corpus.words.words())
		name = username.lower().replace('.', '')
		# For some reason 'started' is not picked up as a word
		# name = name.replace('ed', '')
		if username == 'started': return True
		if name in english_vocab:
			return True
		return False

	# Extract all tags and hashtags from a caption
	def extract_tags(self, caption):
		hashtag = []
		tag = []
		caption = caption.split()
		for x in caption:
			if x[0] == '#':
				y = ''.join(filter(str.isalpha, x))   	
				hashtag.append(y)
			if x[0] == '@':
				y = ''.join(filter(str.isalpha, x))  
				tag.append(y)
		hashtag = list(dict.fromkeys(hashtag))
		tag = list(dict.fromkeys(tag))
		return hashtag, tag

	# Orders a list from its objects highest occurence to lowest
	def top_occurences(self, mylist, item):
		times = []
		for x in mylist:
			occur = mylist.count(x)
			times.append(occur)
		# Combine 2 lists together to form dic
		res = {mylist[i]: times[i] for i in range(len(mylist))} 
		# Sort dictionary upon the values descending
		sort = dict(sorted(res.items(), key=operator.itemgetter(1), reverse=True))
		occurences = dict(list(sort.items())[0: item])
		return occurences 

	# Checks if a caption contains keywords
	def compare_caption(self, caption, keywords, posts):
		for word in keywords:
			if word in caption:
				info = 	{
					'name' : posts['user']['username'] ,
					'pk' : posts['user']['pk'],
					'#likes' : posts['like_count'],
					'caption' : caption
						}
				return info
		return False

	# Returns all hashtags related to one hashtag. 
	def related_tags(self, hashtag, max):
		tags = self.search_tags(hashtag, 3)
		data = []
		for x in tags:
			try: feed = self.hashtag_feed(x)
			except: continue
			info = self.feed_info(feed, 0)
			for y in info: data.append(y)
		info = {'hashtag' : []}
		for x in data:
			info['hashtag'].extend(x['hashtag'])
		info['hashtag'] = self.top_occurences(info['hashtag'], max)
		return info

	# ---------------------------------------------------------- 
	# ------------------ Primary Functions  -------------------- 
	# ---------------------------------------------------------- 

	# Returns all hashtags related to a list of hashtags
	def find_hashtags(self, hashtag_list, max, old_tags = None):
		info = {}
		for x in hashtag_list:
			y = None
			y = self.related_tags(x, round(max/len(hashtag_list)))
			info[x] = y['hashtag']
		
		# # Append new hashtags too file
		# hashtag_dict = None
		# with open('InstaAutomate/Instagram/hashtags.json') as f:
		# 	hashtag_dic = json.load(f)
		# 	keyword = hashtag_dic[0]
		# 	hashtag_dic[keyword] = hashtag_dic
		# f = open('InstaAutomate/Instagram/hashtags.json', "w")
		# f.write(json.dumps(hashtag_dict))
		# f.close()

		return info

	# Checks all posts from locations that contain keywords
	def location_filter(self, location_search, keywords):
		data = []
		for places in location_search:
			area = self.search_locations(places)
			for locations in area:
				try: 
					with contextlib.redirect_stdout(None):				
						feed = self.location_feed(locations['pk'])
						test = feed['items']
				except : continue
				for posts in feed['items']:
					if not posts['caption'] is None:
						caption = posts['caption']['text']
						print(caption)
					else: continue
					compare = self.compare_caption(caption, keywords, posts)
					if compare != False:
						data.append(compare)
		f = open("Instagram/Data/locations.json","w+")
		f.write(json.dumps(data))
		f.close()
		return True

	# Checks all posts from tags that contain keywords
	def tag_filter(self, tag_search, keywords):
		data = []
		for x in tag_search:
			tag_list = self.search_tags(x, 10)
			for tag in tag_list:
				print(tag)
				try: 
					with contextlib.redirect_stdout(None):				
						feed = self.hashtag_feed(tag)
				except : continue
				for posts in feed['items']:
					if not posts['caption'] is None:
						caption = posts['caption']['text']
						# print(caption)
					else: continue
					compare = self.compare_caption(caption, keywords, posts)
					if compare != False:
						data.append(compare)
		f = open("Instagram/hashtag.json","w+")
		f.write(json.dumps(data))
		f.close()
		return True

	# Pass in a list of people and returns everyone that live within a 
	# certain location. If UserFeed cant be accessed then skip user.
	def get_location(self, userID_list, city, country):	
		result = []
		for id_ in userID_list: 
			try: 
				with contextlib.redirect_stdout(None):
					feed = self.get_userFeed(id_['pk'])
					test = feed['items']
			except: 
				print('Error')
				continue
			for count, post in enumerate(feed['items']):
				try:
					if not 'location' in post: continue
					lng = post['location']['lng']
					lat = post['location']['lat']
					# print(post['caption']['text'])
					location = Nominatim().reverse(str(lat)+', '+str(lng))
					location = location.address.split(',')
					# print(location)
					# print(location[-4].split(), len(location[-4].split()), location[-4].split()[-1])
					try: 
						if len(location[-4].split()) < 2:
							loc_city = location[-4].split()[-1]
						elif len(location[-5].split()) < 2:
							loc_city = location[-5].split()[-1]		
						else:
							loc_city = location[-3].split()[-1]						
					except: loc_city = 'None'
					loc_country = location[-1].split()[-1]
					print(loc_city + ', ' + loc_country)
					for place in city:
						if place in loc_city:
							result.append(id_)
							break
					for place in country:
						if place in loc_country:
							result.append(id_)
							break
				except: print('Post Error')
		return result

	# Returns list of the most followed users in a hashtag
	def users_highFollowers(self, hashtag_list, min_followers):
		result = {}
		for hashtag in hashtag_list:
			tags = self.search_tags(hashtag, 1)
			data = []
			for x in tags:
				try: feed = self.hashtag_feed(x)
				except: continue
				data.append(self.post_followInfo(feed, min_followers))	
			result[hashtag] = data	
		f = open("Instagram/highFollowers.json","w+")
		f.write(json.dumps(result))
		f.close()

	# Returns list of the most liked users in a hashtag
	def users_highLikes(self, hashtag_list, min_likes):
		result = {}
		for hashtag in hashtag_list:
			tags = self.search_tags(hashtag, 10)
			data = []
			print(tags)
			for x in tags:
				try: feed = self.hashtag_feed(x)
				except: continue
				for post in feed['items']:
					if post['like_count'] > min_likes:
						feed_data = {
							'name' : post['user']['username'] ,
							'pk' : post['user']['pk'],
							'#likes' : post['like_count'],
							'hashtag' : x,
							'caption' : post['caption']['text'] 
									}
						data.append(feed_data)
			result[hashtag] = data	
		f = open("Instagram/Data/highLikes.json","w+")
		f.write(json.dumps(result))
		f.close()




