# ENODO_global
Social Risk Analysis

# Required OSS:

Python 3
MongoDB - please make sure the server is running
Required Python packages:

The standard sys, os, logging, time, json
dotenv v. 0.6.4

tweepy v. 3.5.0

pymongo v. 3.3.0

# Required Credentials

Twitter Developer API credentials
Create and load a .env file with your own Twitter credentials in the same directory you will run the script from:

consumer_key=#####

consumer_secret=#####

access_token=#####

access_token_secret=#####

# Runtime Instructions

.env file with Twitter credentials is necessary 

PyMongo will connect to the following local host:
host = 'mongodb://127.0.0.1:27017'
This is hard coded into the script and will need to be changed for a remote host.

Run from the terminal:
$ python social_api.py 3 1.1 Morning
*argv[1] = number of tweets to pull in *argv[2] = sleep time between tweet pulls *argv[3:] = search hashtags or terms
The command will connect 3 times to the Twitter API with 1.1 seconds of rest between connections to record Tweets about morning.

Hashtags are searchable, but the # symbol must be escaped in the terminal:
$ python sns_script.py 100 1.1 \#Morning

Tweets will be stored in the twitterdb database. The collection name will printed to the console.
