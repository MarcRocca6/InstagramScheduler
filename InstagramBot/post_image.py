# /usr/bin/env python
import os
import json
import pyautogui
from datetime import datetime
from time import sleep
from .login_data import *
from Google.global_path import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Retrieves Login Details
login = None
with open('login_data.json') as f:
    login = json.load(f)

# Checks to see if an element is present to determine if webpage loaded
def wait(driver, xclass):
	try:
	    element = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,xclass)))
	except TimeoutException:
	    print("Loading took too much time!")
	    # driver.quit()

def post_post(data):

	# Browser options 
	mobile_emulation = { "deviceName": "Nexus 5" }	
	chrome_options = webdriver.ChromeOptions()	
	chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
	chrome_options.add_argument("--incognito")

	# Establish selenium driver
	driver = webdriver.Chrome(options = chrome_options)
	driver.get('https://www.instagram.com')
	
	# Login
	wait(driver, "//button[contains(text(),'Log In')]")
	login_button = driver.find_element_by_xpath("//button[contains(text(),'Log In')]")
	sleep(3)
	login_button.click()
	sleep(3)

	# Wait until page loads & enter login details
	global login
	wait(driver, "//input[@name='username']")
	username_input = driver.find_element_by_xpath("//input[@name='username']")
	username_input.send_keys(login['username'])
	sleep(3)
	password_input = driver.find_element_by_xpath("//input[@name='password']")
	password_input.send_keys(login['password'])
	sleep(3)
	password_input.submit()
	sleep(3)

	# Clear pop up notifications and wait for page to load
	wait(driver, "//button[contains(text(),'Not Now')]")
	try:
		not_now_btn = driver.find_element_by_xpath("//button[contains(text(),'Not Now')]")
		not_now_btn.click()
		sleep(3)
	except:
		sleep(3)

	# Select and open file
	wait(driver, "//div[@role='menuitem']")
	new_post_btn = driver.find_element_by_xpath("//div[@role='menuitem']").click()
	sleep(2)
	pyautogui.write(resource_path('Data/Photos/' + data['path']), interval = 0.08)  
	sleep(2)
	pyautogui.press('enter')
	sleep(3)

	# Upload file
	wait(driver, "//button[contains(text(),'Next')]")
	next_btn = driver.find_element_by_xpath("//button[contains(text(),'Next')]").click()
	sleep(3)

	# Write caption and send
	wait(driver, "//textarea[@aria-label='Write a caption…']")
	caption_field = driver.find_element_by_xpath("//textarea[@aria-label='Write a caption…']")
	for text in data['caption'].split('\\n'):
		caption_field.send_keys(text)
		caption_field.send_keys(Keys.ENTER)

	# Open hashtags
	f = open("InstaAutomate/Instagram/hashtags", "r")
	hashtags = f.read()
	f.close()

	caption_field.send_keys(hashtags)
	sleep(3)
	share_btn = driver.find_element_by_xpath("//button[contains(text(),'Share')]").click()
	
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S")
	print('Posted at ' + current_time)
	wait(driver, "//div[@role='menuitem']")
	sleep(3)
	driver.quit()
	
	os.remove(resource_path("Data/Photos/") + data['path']) # delete uploaded post from local computer