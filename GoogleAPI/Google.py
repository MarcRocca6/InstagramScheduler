#!/usr/bin/python3
# File:             GoogleDrive.py
# Date:             14/06/2021
# Description:      Handles operations on GoogleDrive
# Author:           Marc Rocca
# Modifications:    Null

import os
import json
import re
import urllib.parse
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class Google():
	'''
	Class handling all interactions with Google Drive
	'''
	
	def __init__(self):
		self.drive = self.login()

	def login(self):
		'''
		Performs Authorisation with Google Cloud API
		'''
		gauth = GoogleAuth()
		# Try to load saved client credentials
		pathDir = os.path.join(os.getcwd(), 'Google', 'config')
		gauth.LoadClientConfigFile(os.path.join(pathDir,'client_secrets.json'))
		gauth.LoadCredentialsFile(os.path.join(pathDir,'credentials.json'))

		if gauth.credentials is None:
			# Authenticate if they're not there
			gauth.LocalWebserverAuth()
			# Will stop refresh error by setting access_type offline
			gauth.GetFlow()
			gauth.flow.params.update({'access_type': 'offline'})
			gauth.flow.params.update({'approval_prompt': 'force'})
		elif gauth.access_token_expired:
			# Refresh them if expired
			gauth.Refresh()
		else:
			# Initialize the saved creds
			gauth.Authorize()
		# Save the current credentials to a file
		gauth.SaveCredentialsFile('credentials.json')
		return GoogleDrive(gauth)

	def get_folder_object(self, folder_name):
		'''
		Returns folder object given a folder_name string
		'''
		root_file_list = self.drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
		for file1 in root_file_list:
			if file1['title'] == folder_name:
				return file1

	def upload_image(self, filepath, fileName, folderName=False, folderId=False):
		'''
		Uploads an image to a Google Drive folder given the folders name, 
		a url and filename
		'''
		if folderName != False: folderId = self.get_folder_object(folderName)['id']
		elif folderId == False: raise ValueError("Either folderName or folderId must be passed in.")

		if filepath[-3:] == 'png': imgType = 'png'
		else: imgType = 'jpeg' 
		para = {'title':fileName, 'parents':[{'id':folderId}], 'mimeType':f'image/{imgType}'}
		file_drive = self.drive.CreateFile(para)
		file_drive.SetContentFile(filepath)
		file_drive.Upload()

	def upload_folder(self, folder_name):
		'''
		Uploads an empty folder in the root directory of Google Drive
		given a folder name
		'''
		para = {'title' : folder_name, 'mimeType' : 'application/vnd.google-apps.folder'}
		folder = self.drive.CreateFile(para)
		folder.Upload()
		return dict(folder)['id']

	def get_folder_contents(self, folderID = False, folderName=False):
		'''
		Returns the file objects that are in a folder given that folders name.
		Do not pass in a folderName if you wish to get the contents of root directory
		'''
		if folderName != False:
			folderID = self.get_folder_object(folderName)['id']
		elif folderID != False: pass
		else: folderID = 'root'
		print(folderID)
		para = 	{
				'q': f"'{folderID}' in parents and trashed=false",
				'supportsAllDrives': True,  # Modified
				'includeItemsFromAllDrives': True,  # Added
				}
		
		file_list = self.drive.ListFile(para).GetList()
		return file_list

	def get_folder_content_names(self, folderName=False):
		'''
		Returns string list of the file names inside a folder
		Do not pass in a folderName if you wish to get the contents of root directory
		'''
		file_list = self.get_folder_contents(folderName)
		return [x['title'] for x in file_list]

	def delete_files(self, objectList):
		'''
		Given a list of file objects deletes those 
		objects from Google Drive
		'''
		[x.Delete() for x in objectList]

	def delete_google_folder(self, folderName):
		'''
		Given a folder name string, deletes that folder and its contents
		'''
		self.get_folder_object(folderName).Delete()

	def ready_to_post(self):
		'''
		Scans through all folders in Google Drive to find any that contain 
		only one image, indicating that that post is ready to be uploaded to
		Later.com
		'''
		folders = self.get_folder_contents()
		captionList = [] # Ready To Post List
		folders_to_delete = []
		for f in folders:
			files = self.get_folder_contents(folderID=f['id'])
			# If there are only three files
			print([x['title'] for x in files])
			if len(files) == 3:
				
				print(f"Scheduling {f['title'].replace('_', ' ')} Post")
				folders_to_delete.append(f['title'])
				dirPath = os.path.join(os.getcwd(), 'ImageSearch', 'imgs')
				if not os.path.exists(dirPath): os.makedirs(dirPath)
				postData = {}

				# Iterate through files in folder
				for x in files:
					name, id, mimetype = x['title'], x['id'], x['mimeType']
					# If text file then add '.txt' to end
					if 'text' in mimetype: name = name + '.txt'
					else: postData['Image'] = name # Store image file name

					path = os.path.join(dirPath, name)
					googleFile = self.drive.CreateFile({'id': id})
					googleFile.GetContentFile(path) 

					if 'text' in mimetype:	# If text file then load
						with open(path, 'r', encoding="utf8") as f:
							data = f.read()
						os.remove(path)
						if 'Caption' in name: postData['Caption'] = str(data)
						else: urls = json.loads(data)

				# Get number in image name if present
				imgIndex = re.findall('_(.*)\.', postData['Image'])
				if imgIndex != []: 
					# Use Google's reverse image search to find original image source
					imgUrl = urllib.parse.quote_plus(urls[int(imgIndex[0])-1])
					reverseImgSearch_url = f"https://www.google.com.au/search?q={imgUrl}&tbm=isch"
					result = requests.get(reverseImgSearch_url)
					# Parse out the tag of the original image poster
					soup = BeautifulSoup(result.text, "html.parser")
					website = soup.find_all('span', class_='fYyStc')[1].text
					website = website.replace('www.', '')
					tag = '@'+re.findall('^(.*?)\.', website)[0]
				else: tag = '@'+postData['Image'] # If no number in image name, then tag = image name
				postData['Caption'] = postData['Caption'].replace('_BLANK_', f'{tag}')
				postData['Path'] = postData['Image']
				captionList.append(postData)

		return (captionList)
							
