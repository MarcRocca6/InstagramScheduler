#!/usr/bin/python3
# File:             requestUntapaped.py.py
# Date:             12/06/2021
# Description:      Class that handles all interactions with Untapped.com
# Author:           Marc Rocca
# Modifications:    Null

import os
import re
import requests
import pandas as pd
import Untapped.configuration as config
from requests import get
from bs4 import BeautifulSoup

class requestsUntapped:
	'''
	This class handles interactions with Untapped.com.
	This class extracts all beer information from webpage source code
	'''

	def __init__(self):
		pass

	def extractBeers(self, limit=False, capFlag=True):
		'''
		Create beer captions for a 'limit' of new beers from Untapped.com
		'''
		url = "https://untappd.com/v/midway-cellars/5988012"
		colList = ['Name', 'Caption' , 'Brewer']
		results = requests.get(url, headers=config.headers)
		soup = BeautifulSoup(results.text, "html.parser")
		elements = soup.find_all('div', class_='beer-details')
		df = pd.DataFrame(columns=colList)
		for count, e in enumerate(elements): 
			if limit != False and count >= limit: break
			beerDetails = self.extractDetails(e, capFlag)
			dfDetails = self.addInstaCaption(beerDetails)
			df.loc[count] = dfDetails
			#if capFlag: print(f"Processed {dfDetails[0]}")
		return df

	def extractDetails(self, element, capFlag):
		'''
		Extract specific details for 1 specific beer
		from Untapped webpage source code
		'''
		e = element.find_all('a', class_='track-click')
		btype = str(element.find('em'))[4:-5]
		bname, brewer = tuple([x.text for x in e])
		bname = bname.replace('_', '-')
		abv, ibu = tuple(element.find('h6').text.split('•')[:2])
		url = 'https://untappd.com' + e[0].get('href')
		if capFlag: caption = self.extractCaption(url)
		else: caption = False
		return [str(bname), btype, abv[:-5], ibu[1:-5], brewer, caption]
		
	def extractCaption(self, url):
		'''
		Extract caption information for Untapped.com about 1 specific beer
		'''
		results = requests.get(url, headers=config.headers)
		soup = BeautifulSoup(results.text, "html.parser")   
		caption = soup.find('div', class_='beer-descrption-read-less').text[:-10]
		return caption.replace('\n', '')

	def addInstaCaption(self, beerDetails):
		'''
		Create an Instagram caption and add it to the beer details list.
		'''
		(bname, btype, abv, ibu, brewer, description) = tuple(beerDetails)
		if description == False: return [bname, False, brewer]
		hashtags = self.getHashtags(btype)
		brewerTag = self.getBrewerTag(brewer)

		if abv != 'N/A': abv = f'ABV: {abv}. '
		else: abv = ''
		if ibu != 'N/A': ibu = f'IBU: {ibu}. '
		else: ibu = ''
		if description != '': description = f'{description}'
		else: description = ''

		instaCapt = f'''{brewer} 🍺 {bname}
						\n{description}{abv}{ibu}\n{brewerTag}
						\n🛒Check out this new {btype} available in-store at @midwaycellars
						\n📸 Photo by: _BLANK_\n\n{hashtags}'''
		print(bname)
		return [str(bname), instaCapt, brewer]

	def getBrewerTag(self, brewer):
		'''
		Get the Instagram tag of the beers brewer
		'''
		brewer = brewer.replace('&', 'and') + ' Instagram'
		url = 'https://www.google.com/search?q=' + '+'.join(brewer.split())
		results = requests.get(url, headers=config.headers)
		soup = BeautifulSoup(results.text, "html.parser")
		elements = soup.find_all('h3', class_='LC20lb DKV0Md')
		for e in elements[:6]:
			if e != None:
				pageText = e.text
				reSearch = re.search("([@])\w+", pageText)
				if reSearch != None: return reSearch.group()
		return '' # No tag found

	def getHashtags(self, btype):
		'''
		Returns list of hashtags to use for a particular beer type
		'''
		beerTags = list(dict.fromkeys(self.beerHashtag(btype)))
		beerTags = ['#'+x for x in beerTags]
		otherTags = ['#sydneybeer', '#aussiebeer', '#aussiecraftbeer', '#craftbeer', '#hops', '#indiebeer', 
		'#beerstagram', '#beerpics', '#beeroclock', '#beergeek', '#beer', '#hazybeer', '#craft', '#craftbeer', '#beer',  
		'#goodbeer', '#australianbeer', '#hazybeer', '#drinkfresh', '#drinkgoodbeer', '#drinklocal', '#beerme', '#beerporn']
		return ' '.join([beerTags + otherTags][0])

	def beerHashtag(self, btype):
		'''
		Given a beer type calculates the most popular hashtag for that beer
		'''
		LHS, RHS = btype.split(), None
		LHS = [s.replace('-','') for s in LHS if (s!="Other" and s!="International")]
		e_index = self.charIndex(LHS, '') 			# If contains '', previously ' - '
		d_index = self.charIndex(LHS, '/') 			# If contains '/'
		if e_index != False: 						# If IS ' - ' item
			LHS, RHS = LHS[:e_index], LHS[e_index+1:]
		elif d_index != False: 						# If NO ' - ' item && IS '/' item
			return [''.join(LHS[d_index+1:]),''.join(LHS[:d_index])]
		if d_index == False and e_index == False: 	# If NO ' - ' item && NO '/' item
			return [''.join(LHS)]
		elif d_index != False:						# If IS ' - ' item && IS '/' item
			d_index = self.charIndex(RHS, '/')
			dLHS, dRHS = RHS[:d_index], RHS[d_index+1:]
			return [''.join(LHS), ''.join(dLHS + LHS), ''.join(dRHS + LHS)]
		else: 										# If IS ' - ' item && NO '/' item
			return [''.join(LHS), ''.join(RHS + LHS)]

	def charIndex(self, list_, substring):
		'''
		Given a list, return the index of a particular substring
		'''
		for count, x in enumerate(list_):
			if x == substring: return count
		return False
