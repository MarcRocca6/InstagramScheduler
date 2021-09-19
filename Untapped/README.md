# Untapped.com Module

This module deals with retrieving information from the [Untapped.com](https://untappd.com/) website using HTTP requests. Untapped.com is a networking service website that allows:
* *bottleshops* to upload their recent beer stock 
* *users* to discuss beers they have recently drunk

This module was used to retrieve information and create beer descriptions on the latest beers that have been uploaded by a specific bottleshop.

## File Structure

This module is separated into three files:

1. **Untapped.py**
    * This file saves and retrieves the information extracted from the requestsUntapped.py module into CSV files.
2. **requestsUntapped.py**
    * This file handles all interactions with the Untapped.com website as well as the formation of beer descriptions.
3. **configuration.py**
    * This file contains the HTTP header information that were passed with each HTTP request.  