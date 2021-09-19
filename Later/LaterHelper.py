#!/usr/bin/python3
# File:             LaterHelper.py
# Date:             13/06/2021
# Description:      Helper functions for preprocessing
# Author:           Marc Rocca
# Modifications:    Null

import re
import os
import json
import datetime

class LaterHelper():
	'''
	Class containing helper functions to process data 
	from the LaterAPI
	'''

	def __init__(self): pass

	def updateCookie(self, response, header):
		cookie = response.headers['Set-Cookie']
		header['Cookie'] = cookie
		time = re.findall('expires=(.*) GMT', cookie)[0][5:]
		path = os.path.join(os.getcwd(), 'Later', 'json', 'cookie.json')
		with open(path, "w+") as f:
			json.dump({'Header': header, 'Expiry': time}, f)
		return header

	def imgData(self, x): 
		'''Parse uploaded image data'''
		return {
				'Id' : x['id'],
				'Height': x['height'],
				'Width': x['width'],
				'TimeCreated':x['created_time'], 
				'UpdatedTime':x['updated_time'],
				'Url': x['image_url'],
				'Thumbnail':f"{x['image_url']}?{x['updated_time']}"
				}

	def loadJson(self, filename):
		path = os.path.join(os.getcwd(), 'Later', 'json', filename)
		if not os.path.isfile(path): 
			raise ValueError("Invalid Path: ", path)
		f = open(path,)
		json_data = json.load(f)
		f.close()  
		return json_data 

	def getTime(self, debug=False):
		'''Given timestamp of last scheduled post from uploadedPosts.json, this
		function returns timestamp of the time to upload the next Instagram post.'''

		schedule = {
					'Weekday' : {
						'Time1' : datetime.time(hour=13, minute=0),
								},
					'Weekend' : {
						'Time1' : datetime.time(hour=11, minute=0),
						'Time2' : datetime.time(hour=18, minute=0)
								} 
					}

		# Load latest timestamp
		timestamp = self.getLastScheduled()['Timestamp']
		if timestamp == None: # If the last scheduled post has been posted
			localDateTime = datetime.datetime.now().astimezone() 
		else: 
			UTCDateTime = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
			localDateTime = UTCDateTime.astimezone()
		localTime = localDateTime.time()
		dayOfWeek = localDateTime.weekday()
		incrementDay = 0

		# Get post time of next post
		if dayOfWeek < 5: # Mon->Fri
			if localTime < schedule['Weekday']['Time1']:
				postTime = schedule['Weekday']['Time1']
			else: 
				incrementDay += 1
				if dayOfWeek == 4: postTime = schedule['Weekend']['Time1']
				else: postTime = schedule['Weekday']['Time1']             
		elif dayOfWeek >= 5: # Sat->Sun
			if localTime < schedule['Weekend']['Time1']:
				postTime = schedule['Weekend']['Time1']
			elif localTime < schedule['Weekend']['Time2']:
				postTime = schedule['Weekend']['Time2']
			else: 
				incrementDay += 1 
				if dayOfWeek == 6: postTime = schedule['Weekday']['Time1']
				else: postTime = schedule['Weekend']['Time1']    
		else: raise ValueError("Invalid Day: ", localTime)    
		
		postDay = localDateTime + datetime.timedelta(days=incrementDay)
		postDateTime = datetime.datetime.combine(postDay, postTime)
		timestamp = int(postDateTime.timestamp())
		if debug:
			print(f"Input:\t{localDateTime.strftime('[ %H:%M ]  [ %d-%b-%Y ]')}")
			print(f"Output:\t{postDateTime.strftime('[ %H:%M ]  [ %d-%b-%Y ]')}")
			print(f"Output:\t{timestamp}")
		return timestamp