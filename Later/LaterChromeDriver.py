#!/usr/bin/python3
# File:             LaterChromeDriver.py
# Date:             12/06/2021
# Description:      Uploads images to Later.com
# Author:           Marc Rocca
# Modifications:    Null

import re
import os
import datetime
import pyautogui
from time import sleep
from selenium import webdriver
from datetime import datetime, timedelta
from requests.models import HTTPBasicAuth
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LaterChromeDriver():
	''' 
	Class governing the Selenium ChromeDriver functions.
	Primarily used for uploading images to Later.com
	'''
	
	def __init__(self):
		self.driver = None

	def wait(self, xpath, time):
		'''
		Wait until xclass element appears in selenium driver
		'''
		try: element = WebDriverWait(self.driver,time).until(EC.presence_of_element_located((By.XPATH,xpath)))
		except TimeoutException: print("Loading took too much time.")

	def find_all(self, xpath):
		'''
		Executes self.driver.final_elements_by().\n
		Waits for xpath element to appear else raise error.\n
		@xpath = xpath element string
		'''
		self.wait(xpath,10)
		return self.driver.find_elements_by_xpath(xpath)

	def clear_popup(self):
		try: self.find("//button[@class='o--alert__dismiss']").click()
		except: return 
		while True:
			try: self.find("//button[@class='o--alert__dismiss']", time=2).click()
			except: break

	def find(self, xpath, time = 10):
		'''
		Executes self.driver.find_element_by_xpath().\n
		Waits for xpath element to appear else raise error.\n
		@xpath = xpath element string
		'''
		self.wait(xpath,time)
		return self.driver.find_element_by_xpath(xpath) 		

	# def get(self, url):
	# 	'''
	# 	Executes self.driver.get() to redirect driver.\n
	# 	@url = url string to redirect driver too
	# 	'''
	# 	return self.driver.get(url)

	def setupDriver(self, header=False, headless=False):
		'''
		Establishes the ChromeDriver driver.\n
		@headless = True for headless browser\n
		@header = Can contain browser cookie
		'''
		options = webdriver.ChromeOptions()
		if headless: options.add_experimental_option("headless")
		options = webdriver.ChromeOptions()
		options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
		options.add_experimental_option("excludeSwitches", ["enable-automation"])
		options.add_experimental_option('useAutomationExtension', False)
		options.add_argument('--disable-blink-features=AutomationControlled')
		options.add_argument("--disable-blink-features=AutomationControlled")
		path = os.path.join(os.getcwd(), 'Later', 'chromedriver', 'chromedriver.exe')
		self.driver = webdriver.Chrome(path, options=options)
		if header != False:
			self.driver.get('https://app.later.com') # Get dummy webpage
			cookie = re.findall("=([^;]*)", header['Cookie'])[0]
			self.driver.add_cookie({"name": "_latergram_session", "value": cookie})
			#self.driver.add_cookie(cookie)
		self.driver.get('https://app.later.com/1V68W/schedule/calendar')

	def uploadImgs(self, authHeader):
		'''
		Uploads images to Later.com.\n
		@imgPath = Path of local images to upload
		'''
		self.setupDriver(header=authHeader)
		if self.driver != None: 
			# Remove popup if present
			self.clear_popup()

			# Click 'Upload Button'
			self.find("//div[@class='cUP--upload__text is--base']").click()
			sleep(1) # Wait for element to appear 

			# Enter images paths into Folder GUI and upload
			dir = os.path.join(os.getcwd(), 'ImageSearch', 'imgs', 'post')
			pyautogui.write(dir, interval = 0.01)  
			pyautogui.press('enter')	
			sleep(0.5)		

			# Enter images paths into Folder GUI and upload
			imgNames = os.listdir(dir)
			imgStr = " ".join([f"\"{x}\" " for x in imgNames])
			pyautogui.write(imgStr, interval = 0.01)  
			print(imgStr)
			sleep(0.02)	
			pyautogui.press('enter')

			# Wait for upload to be complete then delete files
			print("Uploading to Later.com ...")
			#sleep(5)
			#self.driver.close()


