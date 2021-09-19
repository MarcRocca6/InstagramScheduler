#!/usr/bin/python3
# File:             GUI.py
# Date:             20/09/2021
# Description:      Creates a Graphical User Interface allowing users to 
#					interact with the features of this repository
# Author:           Marc Rocca
# Modifications:    Null

import os
import io
import sys
import time
import requests
import webbrowser
import pandas as pd
from PIL import Image
from time import sleep
import PySimpleGUI as sg
from shutil import copyfile
from Instagram import Instagram
from ImageSearch.ImageSearch import ImageSearch 

cwd = ''
sys.stderr = open('Error.txt', 'w+')
sys.stdout = open('Output.txt', 'w+')

def main():
	"""
	Controls the Graphical User Interface of this application
	"""

	driver = Instagram()
	caption = None
	beer_df = driver.Untapped.loadBeers()
	data = beer_df[['Name', 'Brewer']].values.tolist()

	sg.theme('DarkAmber')
	font = ('Courier New', 11)
	headings = ['Brand', 'Name']

	layout = [
		[
			sg.Text('The Beer Scheduler', justification='center', size = (60,2), key='-text-', font=("Courier New", 20))
		],
		[
			sg.Frame('Beers To Schedule',
				[
					[
						sg.Table(
							values=data,                # Empty data must be with auto_size_columns=False
							headings=headings,
							auto_size_columns=False,    # For empty data
							vertical_scroll_only=True,	# Required if column widths changed and width of table not changed
							hide_vertical_scroll=True,  # Not required if no more rows of data
							def_col_width=20,
							num_rows=12,
							col_widths=[25,25],      	# Define each column width as len(string)+2
							font=font,                  # Use monospaced font for correct width
							justification="left",
							pad=(10,15),
							key='-TABLE-'),
					], 
					[
						sg.Button('Open Later.com', size = (13, 1) , pad=(10,20), tooltip = 'Opens up Later.com'),
						sg.Button('Update Beers', size = (13, 1), pad=(10,10), tooltip = 'Updates the beer list from Untapped.com'),
						sg.Button('Load Post', size = (10, 1), pad=(10,10), tooltip = "Loads the post details for the selected beer"),
					],
				], pad=(20,10), element_justification='left', vertical_alignment='t', font = font
			),
			sg.Frame('Post Data',
				[
					[
						sg.Text('Caption:', pad=(10,15), justification='left', font = font),
						sg.Multiline(size=(63, 10), key='-TEXT-', autoscroll=True, pad=(10,15))
					],
					[
						sg.Text('Image:  ', pad=(10,15), justification='left', font = font),      
						sg.Input(do_not_clear=True, pad=(5,15), enable_events=True, key = '-URL-'),  
						sg.FileBrowse(pad=(10,15), change_submits=True, tooltip = "Browse your computer to find a suitable image",
										file_types=[("JPEG (*.jpg)", "*.jpg"),("All files (*.*)", "*.*")]),    
						sg.Button('Read URL', pad=(10,15), tooltip= "If a URL was entered, accepts that URL as the image."), 
					],
					[
						sg.Image(data=None, size=(None,None), key='-DISPLAY-', visible=False)
					],
					[
						sg.Button('Sample Images', pad=(10,30),
								tooltip = 'Displays images of the selected beer that are options for the post image'),
						sg.Button('Google Images', pad=(10,30),
								tooltip = 'Opens up the Google Images results for the selected beer'),
						sg.Button('Open Instagram', pad=(10,30),
								tooltip = "Opens up the Instagram page for the selected beer's Brewer"),
						sg.Button('Schedule Post', pad=(10,30),
								tooltip = "Schedules the post of this selected beer with Later.com")
					],
				], pad=(20,10), vertical_alignment='t', key='-POST-', font = font
			),
		]
	]
	imgSearch = ImageSearch()
	window = sg.Window('Beer Scheduler', 	layout, grab_anywhere=True, margins=(10,10), icon=cwd+'beers.ico', finalize=True, 
											resizable = True, auto_size_buttons=True, auto_size_text=True, location = (450,50))
	while True:
		event, values = window.read()
		#print(event, values)
		if event == sg.WIN_CLOSED or event == 'Cancel': break
		elif event == 'Read URL': 
			if caption == None:
				error('Please select a beer first.')
			else:
				display_img(window, url=values['-URL-'])
		elif event == '-URL-' and len(values['Browse']) > 5:
			display_img(window, path=values['-URL-'])
		elif event == 'Sample Images':
			if caption == None:
				error('Please select a beer first.')
			else:
				beerName = caption.split('\n')[0].replace('🍺', '')
				urls = imgSearch.getURLs(beerName, '')
				url = img_gallery(urls)
				if url != None: 
					window['-URL-'].Update(value = url)
					display_img(window, url=url)
		elif event == 'Update Beers': 
			layout2 = [[sg.Output(size=(80, 10), key='-OUTPUT-', pad=(20,20), echo_stdout_stderr=True)]]
			window2 = sg.Window('Loading New Beers', layout2, icon=cwd+'beers.ico', finalize=True)
			driver.getNewBeers(limit=8, numImgs=0)
			beer_df = driver.Untapped.loadBeers()
			data = beer_df[['Name', 'Brewer']].values.tolist()
			window['-TABLE-'].Update(values = data)
			window2.Close()
		elif event == 'Load Post':
			row = values['-TABLE-']
			if row == []:
				error('Please select a beer first.')
			else:
				beerDetails = beer_df.iloc[row]
				caption = beerDetails[['Caption']].values.tolist()[0][0]
				window['-TEXT-'].Update(value=caption)
		elif event == "Open Instagram":
			if caption == None:
				error('Please select a beer first.')
			else:
				username = [w for w in caption.split() if '@' in w][0][1:]
				url = f"https://www.instagram.com/{username}/"
				chrome = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
				webbrowser.get(chrome).open(url)
		elif event == "Open Later.com":
			url = f"https://app.later.com/1V68W/schedule/calendar"
			chrome = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
			webbrowser.get(chrome).open(url)
		elif event == "Google Images":
			if caption == None:
				error('Please select a beer first.')
			else:
				beerName = caption.split('\n')[0].replace('🍺', '')
				url = f"https://www.google.com/search?q={beerName}&tbm=isch"
				chrome = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
				webbrowser.get(chrome).open(url)
		elif event == 'Schedule Post':
			if values['-URL-'] == '': 
				error('Please upload an image.')
			else:
				caption = values['-TEXT-']
				url = values['-URL-']
				path=os.path.join(os.getcwd(),'ImageSearch','imgs','post', 'GUI_Beer.jpg')
				try: # if local file
					copyfile(values['Browse'], path)
				except: # if URL
					r = requests.get(url, allow_redirects=True)
					print(os.path.isfile(path))
					open(path, 'wb').write(r.content)
				driver.Later.uploadImgs()
				while True:
					recent = driver.Later.recentCreated(2)
					if recent >= 1: break
				driver.Later.chrome.driver.close() 
				LaterImage = driver.Later.uploadedImgsInfo(debug=False, limit=10)[0]
				LaterImage['Caption'] = caption
				driver.Later.schedulePost(LaterImage)
				del data[values['-TABLE-'][0]]
				window['-TABLE-'].Update(values=data)
				beer_df = beer_df.drop([beer_df.index[values['-TABLE-'][0]]])
				driver.Untapped.saveBeers(beer_df)
				beerDetails = beer_df.iloc[row]
				caption = beerDetails[['Caption']].values.tolist()[0][0]
				window['-TEXT-'].Update(value=caption)
				window['-URL-'].Update(value = '')
				window.Element('-DISPLAY-').Update(visible=False)
	window.Close()


##################################
######## Helper Functions ########
##################################


def error(text):
	"""
	Displays Error Popup
	"""
	layout = [[sg.Text(text, justification='center', pad=(10,10))],
			[sg.Button('OK', size = (10, 1), pad=(10,10))]]
	error_win = sg.Window(' ', layout, grab_anywhere=True, location=(900,250), margins=(10,10), icon=cwd+'beers.ico')
	while True:
		event, values = error_win.read()
		if event == sg.WIN_CLOSED or event == 'OK': break
	error_win.Close()

def img_gallery(url_list):
	"""
	Display Image Gallery Popup
	"""
	i = 0
	length = len(url_list)
	layout = [[sg.Text(f"Image 1/{length}", justification='center', key='-TXT-', pad=(10,10))],
			[sg.Image(data=None, size=(None,None), key='-DISPLAY-')],
			[sg.Button('Prev', size = (10, 1), pad=(10,10)), 
			sg.Button('Choose', size = (10, 1), pad=(10,10)),
			sg.Button('Next', size = (10, 1), pad=(10,10))]]
	win = sg.Window('Select Image', layout, location=(900,250),grab_anywhere=True, margins=(10,10), finalize=True, icon=cwd+'beers.ico')
	display_img(win, url = url_list[i])
	while True:
		event, values = win.read()
		if event == sg.WIN_CLOSED: 
			win.Close()
			return None
		elif event == 'Choose': 
			win.Close()
			return url_list[i]
		elif event in ('Next', 'MouseWheel:Down') and i < len(url_list)-1:
			i += 1
			win.Element('-TXT-').Update(value = f"Image {i+1}/{length}")
			display_img(win, url = url_list[i])
		elif event in ('Prev', 'MouseWheel:Up') and i > 0:
			i -= 1
			win.Element('-TXT-').Update(value = f"Image {i+1}/{length}")
			display_img(win, url = url_list[i])

def display_img(window, path=None, url=None, baseheight=400):
	"""
	Display an image given a path or a URL
	"""
	try:
		img = None
		if url != None: 
			response = requests.get(url, stream=True)
			img = Image.open(io.BytesIO(response.content))
		elif path != None: 
			img = Image.open(path)
		wpercent = (baseheight/float(img.size[1]))
		wsize = int((float(img.size[0])*float(wpercent)))
		img = img.resize((wsize,baseheight), Image.ANTIALIAS)
		bio = io.BytesIO()
		img.save(bio, format="PNG")
		img_data = bio.getvalue()
		window.Element('-DISPLAY-').Update(data=img_data)
		window.Element('-DISPLAY-').Update(visible=True)
	except: 
		window.Element('-DISPLAY-').Update(visible=False)
		error('Error. Invalid image path')

if __name__ == "__main__":
	main()