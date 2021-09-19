#!/usr/bin/python3
# File:             LaterAPI.py
# Date:             12/06/2021
# Description:      Handes all interactions with Later.com website
# Author:           Marc Rocca
# Modifications:    Null

import os
import re
import requests
import pandas as pd
from requests import get
from bs4 import BeautifulSoup
from Untapped.requestsUntapped import requestsUntapped

class Untapped(requestsUntapped):
	'''
	This class handles all storing & processing of the beer
	information requested by the parent class requestUntapped
	'''
	
	def __init__(self):
		requestsUntapped.__init__(self) 	

	def getNames(self):
		'''
		Get names of all recently uploaded beers from Untapped
		'''
		return self.extractBeers(capFlag=False)[['Name']]

	def getBeers(self):
		'''
		Get details of all recently uploaded beers from Untapped
		'''
		return self.extractBeers(capFlag=True)

	def saveNames(self, df): 
		'''
		Save beer names into beerDetails.csv. This csv file contains a list 
		of beers that have been processed and have had their details extracted
		'''
		path = os.path.join(os.getcwd(), 'Untapped', 'csv', 'beerNames.csv')
		self.saveCSV(df, path)

	def saveBeers(self, df): 
		'''
		Save beer details into beerDetails.csv. This csv file contains 
		a list of beer details that have not been scheduled for posting.
		'''
		path = os.path.join(os.getcwd(), 'Untapped', 'csv', 'beerDetails.csv')
		self.saveCSV(df, path)

	def saveCSV(self, df, filename):
		'''
		Save dataframes into csv files
		'''
		df.drop_duplicates(inplace=True, ignore_index=True)
		df.to_csv(filename)		

	def loadNames(self): 
		'''
		Load data from the beerNames.csv file
		'''
		path = os.path.join(os.getcwd(), 'Untapped', 'csv', 'beerNames.csv')
		if not os.path.isfile(path): 
			return pd.DataFrame(columns=['Name'])
		return pd.read_csv(path, index_col=0)

	def loadBeers(self): 
		'''
		Load data from the beerDetails.csv file
		'''
		path = os.path.join(os.getcwd(), 'Untapped', 'csv', 'beerDetails.csv')
		if not os.path.isfile(path): 
			return pd.DataFrame(columns=['Name', 'Brewer', 'Caption'])
		return pd.read_csv(path, index_col=0)
	
	def addCaption(self):
		'''
		Add captions to beers from beerDetails.csv that dont have a caption
		'''
		captions = self.loadBeers()['Caption'].tolist()
		indexs = [i for i, x in enumerate(captions) if x == 'False']
		print(indexs) # Unfinished Function

	def extractNewBeers(self, limit=False):
		'''
		Extracts beers from Untapped that haven't been processed. Then loads 
		beer names into beerNames.csv and beer details into beerDetails.csv
		'''
		newNames_df, newDetails_df = None, None
		oldNames = self.loadNames()['Name'].tolist()
		newNames = self.getNames()['Name'].tolist()
		for count, new in enumerate(newNames):
			if oldNames == []: count = len(newNames)
			elif new == oldNames[0]: break
		if count != 0:
			if limit != False: count = limit
			df = self.extractBeers(limit=count, capFlag=True)
			newNames_df = pd.concat([df[['Name']], self.loadNames()], ignore_index=True)
			newDetails_df = pd.concat([df, self.loadBeers()], ignore_index=True)
		return {"Names" : newNames_df, "Details" : newDetails_df, "Count": count}