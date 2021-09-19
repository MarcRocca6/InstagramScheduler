#!/usr/bin/python3
# File:             Later.py
# Date:             12/06/2021
# Description:      Handes all interactions with Later.com website
# Author:           Marc Rocca
# Modifications:    Null

import os
import re
import json
import requests
import datetime
from time import sleep
from Later.LaterHelper import LaterHelper
from Later.LaterChromeDriver import LaterChromeDriver

class Later(LaterHelper):
	'''
	Handles all actions that interact with the Later.com API
	'''

	def __init__(self):
		LaterHelper.__init__(self)
		self.chrome = LaterChromeDriver()
		self.s = requests.Session()
		self.authHeader = None 
		self.auth_token = None

	def login(self):
		'''
		Logins into the Later.com website
		'''
		path = os.path.join(os.getcwd(), 'Later' , 'json', 'cookie.json')
		with open(path, 'r+') as f:
			cookieDict = json.load(f)
			expiry=datetime.datetime.strptime(cookieDict['Expiry'],'%d %b %Y %H:%M:%S')
		if datetime.datetime.now() > expiry+datetime.timedelta(hours=9): # as 'expiry' is in GMT time
			# Get configuration token
			getURL = 'https://app.later.com/api/v2/config'
			response = self.s.get(getURL)
			config_token = response.json()['later_config']['authenticity_token']
			#print(response)

			# Enter password & get authorisation token
			postURL = 'https://app.later.com/api/tokens/'
			login_data = self.loadJson('loginTemplate.json')
			login_data['authenticity_token'] = config_token
			response = self.s.post(postURL, json=login_data)
			self.auth_token = response.json()['auth_token']
			#print(response)

			# Get session cookie
			getURL = 'https://app.later.com/api/v2/users/1948882/accounts/'
			self.authHeader = {'Authorization': f'Token token="{self.auth_token}"'}
			response = self.s.get(getURL, headers = self.authHeader)
			self.authHeader = self.updateCookie(response, self.authHeader)
			if response == '<Response [200]>': print('Logged In Succestfully.')
			if response.ok:
				print('Logged In Succestfully.')
			else:
				print(response)
				print(response.text)
				raise ValueError('Logged In Error.')
		else: 
			self.authHeader = cookieDict['Header']
			print('Logged In Succestfully.')


	def getLastScheduled(self, debug=False):
		'''
		Get Last Scheduled Post Data
		'''
		getURL = 'https://app.later.com/api/v2/grams/?social_profile_id=2196633&limit=60&type=preview'
		response = self.s.get(getURL, headers = self.authHeader)
		grams = response.json()['grams']

		lastGram = {'Caption' : None, 'Timestamp': None}
		if grams != []:
			lastGram['Caption'] = grams[-1]['caption']
			lastGram['Timestamp'] = grams[-1]['scheduled_time']
		if debug: print(f'{response}\n{lastGram}')
		return lastGram

	def schedulePost(self, postData):
		'''
		Schedules a post into Later.com for the next predetermined
		posting time.\n
		@caption = String of the caption to post\n
		@imgURL = Url of high resolution image from your Later.com account\n
		@thumbnail = Url of low resolution image from your Later.com account
		'''
		data = self.loadJson('postTemplate.json')
		data['gram']['caption'] = postData['Caption']
		data['gram']['post_media_items'][0]['image_url'] = postData['Url']
		data['gram']['post_media_items'][0]['height'] = postData['Height']
		data['gram']['post_media_items'][0]['width'] = postData['Width']
		data['gram']['post_media_items'][0]['media_item_id'] = postData['Id']
		data['gram']['scheduled_time'] = self.getTime(debug = False)
		postURL = 'https://app.later.com/api/v2/grams/'
		response = self.s.post(postURL, headers = self.authHeader, json=data)
		return response

	def uploadedImgsInfo(self, debug=False, limit=None):
		'''
		Return information on uploaded images
		'''
		getURL = 'https://app.later.com/api/v2/media_items/?group_id=1939740/&limit=48&start_date=2147483647'
		response = self.s.get(getURL, headers = self.authHeader)
		latestImgs = [self.imgData(x) for x in response.json()['media_items']]
		if limit!=None: latestImgs=latestImgs[:limit]
		if debug: 
			print(f"{len(latestImgs)} Images Uploaded")
			print(json.dumps(latestImgs, indent=2))
		return latestImgs

	def recentCreated(self, min):
		'''
		Returns number of images created within a certain number of minutes
		'''
		recentImgs = 0
		imgStamps = [x['TimeCreated'] for x in self.uploadedImgsInfo()]
		for timestamp in imgStamps[:15]:
			cur = int(datetime.datetime.now().timestamp())
			if cur -  timestamp < 60*min: recentImgs += 1
		return recentImgs

	def uploadImgs(self):
		'''
		Uploads local images to the Later.com website using Chrome browser.\n
		@imgData = List of local paths to upload
		'''
		self.login()
		self.chrome.uploadImgs(self.authHeader)