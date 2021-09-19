# Instagram Bot

This module uses an unoffical [Instagram API library](https://github.com/Julian-O/Instagram-API-python) to automate common Instagram actions. 

This [Instagram API library](https://github.com/Julian-O/Instagram-API-python) repository is build off the [Instagram Legacy API](https://www.instagram.com/developer/) which was depreciated by Facebook as of June 29, 2020. Therefore this whole module also became depricated at this time.

## Features

* This module was able to automate actions such as:
    * Get list of people that *Liked* a particular Instagram post
    * Get basic profile information about a particular user such as their username, full-name and number of followers
    * Get the latest posts in the logged in users *Instagram Feed*
    
    * Given a list, follows or unfollows all the users in that list
    * Unfollows all the users that are not current following the logged in user
    * *Like* the last 3 posts from a particular user
    * *Comment* on the last post of a particular user
    * Determine the most popular hashags related to a particular keyword
    * Returns the a list of the most liked users that relate to a particular hashtag
    * Determine the location of a list of users by using the GeoTags in their posts
    * Return the users that follow a particular user
    * Returns the latest Instagram notifications for the logged in user


## File Structure

This module is separated into three files:

1. **InstaBot.py**
    * This file utilises the [Instagram API library](https://github.com/Julian-O/Instagram-API-python) to interact with the [Instagram Legacy API](https://www.instagram.com/developer/) 
2. **post_images.py**
    
    * This uses browser automation using [selenium](https://selenium-python.readthedocs.io/) to post an image onto Instagram 
3. **post_hashtags.py**
    * This uses browser automation using [selenium](https://selenium-python.readthedocs.io/) to comment on a particular Instagram post. 

