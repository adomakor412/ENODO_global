# ENODO_global
Social Media API

This is well tested for UNIX and UBuntu users
Required OSS:

Python 3 - note your /usr/bin/env
MongoDB - please make sure the server is running
Required Python packages:

The standard sys, os, logging, time, json
dotenv v. 0.6.4, found here
tweepy v. 3.5.0, found here
pymongo v. 3.3.0
Required Credentials

Twitter Developer API credentials
Create and load a .env file with your own Twitter credentials in the same directory you will run the script from:
consumer_key=#####
consumer_secret=#####
access_token=#####
access_token_secret=#####
Note the capitalization you are using

Runtime instructions

.env file with Twitter credentials is necessary as shown above
PyMongo will connect to the following local host:
host = 'mongodb://127.0.0.1:27017'
This is hard coded into the script and will need to be changed for a remote host.
Run from the terminal:
$ python sns_script.py 25 1.1 Baseball
*argv[1] = number of tweets to pull in *argv[2] = sleep time between tweet pulls *argv[3:] = search hashtags or terms
The command will connect 25 times to the Twitter API with 1.1 seconds of rest between connections to record Tweets about baseball
Hashtags are searchable, but the # symbol must be escaped in the terminal:
$ python sns_script.py 100 1.1 \#Baseball
Tweets will be stored in the twitterdb database. The collection name will printed to the console.
Debugging

The script includes a logger which writes to a *.log file in the same directory as the script. The default setting is debug. It is recommended to delete logs regularly if harvesting many tweets.
