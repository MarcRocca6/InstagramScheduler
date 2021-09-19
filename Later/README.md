# Later.com Module

This module deals with retrieving and passing information to the Later.com API. Later.com is a social media management tool that allows you to schedule posts across platforms such as Instagram and Facebook. 

Interactions with the Later.com API are performed using HTTP requests and Browser Automation through the use of the python module Selenium. 

## File Structure

This module is separated into three files:

1. **Later.py**
    * Handles all HTTP requests with the Later.com API
2. **LaterHelper.py**
    * Contains helper functions for *Later.py* such as saving and loading cookies
3. **LaterChromedriver.py**
    * Handles the browser automation that interacts with the Later.com API such as uploading images.

## API Interactions

The [mitmproxy](https://github.com/mitmproxy/mitmproxy) repository was used to perform a [Man in the Middle Attack](https://en.wikipedia.org/wiki/Man-in-the-middle_attack) on an android device that interacted with the Later.com website. By reading the requests sent and received from the API, the appropriate requests were able to be found to perform functions such as: 
+ Logging In
+ Scheduling an Instagram Post
+ Retrieving Data on Uploaded Images

## Browser Automation

There was one function that was unable to be implemented by using HTTP requests and that was the uploading of an image to the Later.com servers. Later.com utilised *AWS (Amazon Web Services)* and therefore an encryption was required to be able to upload files such as images to their servers. Therefore the only way to autonomously upload images to the Later.com servers was to use *Browser Automation* to upload the image through Later.com website.

The [selenium](https://selenium-python.readthedocs.io/) library and [chromedriver](https://chromedriver.chromium.org/downloads) were used to perform this browser automation to upload images to the servers.

