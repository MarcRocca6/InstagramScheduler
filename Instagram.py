import sys
import os
import click
from time import sleep
from Later import Later
from Untapped import Untapped 
from ImageSearch import ImageSearch

class Instagram():
	'''
	Handles all Instagram resource searching and scheduling
	'''
	
	def __init__(self):
		self.Later = Later.Later()
		self.Untapped = Untapped.Untapped()
		self.ImageSearch = ImageSearch.ImageSearch()

	def getNewBeers(self, limit=False, numImgs=7):
		'''
		Creates captions for newly uploaded beers & finds
		potential Instagram photos for each beer
		'''
		print("\nFinding New Beers & Creating Captions.\n")
		beerDict = self.Untapped.extractNewBeers(limit=limit)
		count = beerDict['Count']
		if count == 0: return print("No new beers uploaded.\nCompleted.")
		beerDetails = beerDict['Details'] # beer details df
		names = beerDetails['Name'].tolist()[:count]
		brewers = beerDetails['Brewer'].tolist()[:count]
		captions = beerDetails['Caption'].tolist()[:count]

		if numImgs != 0: 
			print("\nCreated All Captions.\nFinding Images.\n")
			for count, name in enumerate(names):
				brewer = brewers[count]
				caption = captions[count]
				if numImgs != 0: print(f"Uploading {name} Images.")
				imgURLs=self.ImageSearch.getImgs(name,brewer,caption,toDownload=numImgs)
				beerDetails.at[count, 'Urls'] = " ".join(imgURLs)
		self.Untapped.saveNames(beerDict['Names'])
		self.Untapped.saveBeers(beerDetails)
		print("\nCompleted.\n")

	def uploadPost(self):
		'''
		Schedules beer posts to Later.com
		'''
		df = self.Untapped.loadBeers()
		originList = self.ImageSearch.ready_to_post(df)
		toPost = len(originList)

		if toPost != 0:
			self.Later.uploadImgs()

			tagList = []
			postDir = os.path.join(os.getcwd(), 'ImageSearch', 'imgs', 'post')
			postFilenames = os.listdir(postDir)
			postBeers = [x.replace('_', ' ')[:-4] for x in postFilenames]
			for count,beer in enumerate(postFilenames):
				beerPath = os.path.join(postDir,beer)
				tag = self.ImageSearch.find_original(beerPath, originList[count])
				tagList.append({'name':beer[:-4], 'tag':tag})
				print(tag)
			self.ImageSearch.add_photoTag(tagList)

			while True:
				recent = self.Later.recentCreated(2)
				if recent >= toPost: break
			print(f"Succestfully uploaded {toPost} files to Later.com")
			self.Later.chrome.driver.close() # Turn off chromedriver

			df = self.Untapped.loadBeers()
			LaterImages = self.Later.uploadedImgsInfo(debug=False, limit=10)[:toPost]
			for count, post in enumerate(LaterImages):
				post['Caption']=list(df.loc[df['Name']==postBeers[count],"Caption"].values)[0]
				self.Later.schedulePost(post)
			print(f"Scheduled {toPost} Posts in Later.com")
			
			[os.remove(os.path.join(postDir,x)) for x in postFilenames]
		else: print("No Posts Ready to Upload.")

