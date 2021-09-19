#!/usr/bin/python3
# File:             ImageSearch.py
# Date:             12/06/2021
# Description:      Locates images related to a given query
# Author:           Marc Rocca
# Modifications:    Null

import os
import re
import json
import shutil
import glob
import requests
import urllib.parse
import pandas as pd
from requests import get
from datetime import datetime
#from Google import Google
from bs4 import BeautifulSoup
import Untapped.configuration as config

class ImageSearch():
	'''
	Given a query keyword, downloads relevant images from Google.com
	'''

	def __init__(self): pass

	def getURLs(self, name, brewer):
		'''
		Given a beer name and a brewer, returns a list of urls of
		of that beer found from Google Images.
		'''
		beerQuery = urllib.parse.quote_plus(f"{brewer} {name}")
		url = f"https://www.google.com/search?q={beerQuery}&tbm=isch"
		results = requests.get(url, headers=config.headers).text
		regex = re.findall(r'"(https:((?!").)*(png|jpg))"', results)
		#print(len(regex))
		imgURLs = []
		for r in regex: 
			(url,_,_) = r
			#id = re.findall('"(.{14})"',id_r)[0]
			#print(url)
			imgURLs.append(url)
		return imgURLs

	def downloadImgs(self, urls, name, debug=False):
		'''
		Given a list of urls, downloads the images into the './ImageSearch/imgs'
		directory.
		'''
		name = str(name).replace(' ', '_')
		#name = re.findall('(\w+?)[\W]*$', name)[0]
		for count,url in enumerate(urls):
			folder = os.path.join(os.getcwd(), 'ImageSearch' , 'imgs', f'{name}')
			if not os.path.exists(folder): os.makedirs(folder)
			filename = os.path.join(folder, f'{count+1}{url[-4:]}')
			r = requests.get(url, allow_redirects=True, headers=config.headers)
			open(filename, 'wb').write(r.content)
			if debug: print(f'{count+1} Images Downloaded')
		print()

	def ready_to_post(self, df):
		'''
		Check if there are images ready to post.
		If there is only 1 image in a image folder then move
		that image to the directory 'imgs/post'. 
		Return True if there is an image ready to post else
		return False
		'''
		cwd = os.getcwd()
		imgDir = os.path.join(cwd, 'ImageSearch' ,'imgs')
		postDir = os.path.join(imgDir , 'post')
		rel_beerDirs = os.listdir(imgDir)
		rel_beerDirs.remove('post')
		beerDirs = [os.path.join(imgDir,x) for x in rel_beerDirs]
		originList = []
		for count,folder in enumerate(beerDirs):
			
			pngFiles = glob.glob(os.path.join(folder, '*.png'))
			jpegFiles = glob.glob(os.path.join(folder, '*.jpg'))
			imgFiles = pngFiles+jpegFiles
			numImgs = len(imgFiles)
			if numImgs == 1:
				imgName = imgFiles[0]
				fromPath = os.path.join(imgDir,imgName)
				beerName = rel_beerDirs[count].replace("_", " ")
				new_imgName = rel_beerDirs[count] + imgName[-4:]
				toPath = os.path.join(postDir,new_imgName)

				# Calculate Origin from URL 
				urlList=df.loc[df['Name']==beerName,"Urls"].values[0].split(" ")
				try:
					index = int(re.findall("([0-9]+)$", fromPath[:-4])[0])-1
					url = urlList[index]
					origin = re.findall('^http[s]*:\/\/[cdn\.]*[media\.]*[www\.]*(.*?)\.', url)[0]
					if origin in ['images', 'google', 'upload']: origin = "_BLANK_"
					else: origin=str(origin)+'.com'
				except: origin = "_BLANK_"
				originList.append(origin)

				shutil.move(fromPath, toPath)
				# remove remaining files in dir
				[print(os.path.join(folder,x)) for x in os.listdir(folder)]
				[os.remove(os.path.join(folder,x)) for x in os.listdir(folder)]
				os.rmdir(folder) # remove directory
		return originList
		
	def getImgs(self, name, brewer, debug=True, toDownload=7):
		'''
		Uses self.getURLs() to acquire relevant urls, then trims the
		irrelevant urls before calling self.downloadImgs() to download
		those files into  the './ImageSearch/imgs' directory.
		'''
		imgURLs = self.getURLs(name, brewer)
		if len(imgURLs)>toDownload:imgURLs=imgURLs[:toDownload]
		self.downloadImgs(imgURLs, name, debug=debug)
		return imgURLs

	def add_photoTag(self, tagDict):
		'''
		Given an image file's path, gets the tag of the original image posted using
		self.find_original() and then edit beerDetails.csv 'caption' entry to add tag
		'''
		csvPath = os.path.join(os.getcwd(), 'Untapped', 'csv', 'beerDetails.csv')
		df = pd.read_csv(csvPath, index_col=0)
		for tagD in tagDict:
			beerName, tag = tagD['name'].replace("_", " "), tagD['tag']
			captionCell = list(df.loc[df['Name'] == beerName, "Caption"].values)[0]
			newCaption = str(captionCell).replace("_BLANK_", str(tag))
			df.at[df['Name'] == beerName, "Caption"] = newCaption
		df.to_csv(csvPath)		

	def find_original(self, filePath, origin):
		'''
		Suggests the possible website source of an image give its path on the local computer.
		'''
		if origin != "_BLANK_": return origin
		# Get html response of reverse image search
		searchUrl = 'http://www.google.hr/searchbyimage/upload'
		multipart = {'encoded_image': (filePath, open(filePath, 'rb')), 'image_content': ''}
		response = requests.post(searchUrl, files=multipart, allow_redirects=False)
		reverseSearch = requests.get(response.headers['Location'], headers=config.headers)
		soup = BeautifulSoup(reverseSearch.text, "html.parser")
		results = soup.find_all('div', class_='g')
		matchingResults = []

		print(response.headers['Location'])
		results.reverse()
		for result in results:
			rawDimension = result.find('span', class_='MUxGbd wuQ4Ob WZ8Tjf')
			if rawDimension == None: continue
			w = re.findall("^([0-9]+?)\s" , rawDimension.text)
			if w == []: continue
			raw_website = result.find('cite', class_='iUh30 Zu0yb qLRx3b tjvcx')
			if raw_website == None: continue
			website = re.findall('^http[s]*:\/\/[www\.]*(.*?)\.', str(raw_website.text))
			if website == []: website = re.findall('^(.*?)\.', str(raw_website.text))
			else: website = website[0]
			if website in ['twitter', 'instagram', 'facebook']:
				website = re.findall('› (.*)$', str(raw_website.text))[0]
			matchingResults.append((website, int(w[0])))
		# Get website with largest image
		max_w = 0
		max_website = '_BLANK_'
		for website, w in matchingResults: 
			if w > max_w: max_website = website
		#match = dict(sorted(matchingResults.items(), key=lambda x:x[1]))
		#if match == {}: return '_BLANK_'
		#return str(list(match.keys())[-1])+'.com'
		print(str(max_website)+'.com')
		return str(max_website)+'.com'
