"""
@author: kt12
Kenneth Tsuji
2017-07-17

@editor: adomakor12
Kenneth Tsuji
2017-07-17
"""

import sys, os, logging
from dotenv import load_dotenv
import time
import pymongo
import tweepy
import json
# Set number of tweets to record, sleep between API calls, and subject matter

num_tweets = int(sys.argv[1])
sleep = float(sys.argv[2])
subject = sys.argv[3:]
subject_type = (type(subject))

# Append hashtags and de-hashed terms to subject_list
subject_list = []

# Check if input is single string or list of terms or hashtag
if subject_type is str:
    # check hashtag
    if '#' in subject:
        subject_list.extend((subject, subject.replace('#', '')))
    else:
        subject_list.append(subject)

elif subject_type is list:
    # If type is lst and len is 1, must be hashtag
    for k in subject:
        if '#' in k:
            subject_list.extend((k, k.replace('#', '')))
        else:
            subject_list.append(k)

else:
    raise Exception

# Set up logging
logger = logging.getLogger(__name__)
# Logs at debug level will be recorded
logger.setLevel(logging.DEBUG)

# Include STDOUT in log stream
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
logger.addHandler(console_handler)

# Push formatted logs out to .log file
timestamp = time.strftime("%Y%m%d-%H%M%S")
file_handler = logging.FileHandler('twitter_' + timestamp + '.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.debug('Logger initiated.')

# Credentials must be stored in .env file in same directory.
# Load Twitter credentials
load_dotenv('.env')
CONSUMER_KEY = os.environ.get('consumer_key')
CONSUMER_SECRET = os.environ.get('consumer_secret')
ACCESS_TOKEN = os.environ.get('access_token')
ACCESS_TOKEN_SECRET = os.environ.get('access_token_secret')
logger.debug('Twitter credentials loaded.')

print('The topic(s) you chose to track through Twitter: {}.'.format(subject_list))
logger.debug('Topic decided: {}.'.format(subject_list))


# Set MongoDB local host (on same machine)
host = 'mongodb://127.0.0.1:27017'

# Connect to twitterdb
# Will be created if it doesn't exist
client = pymongo.MongoClient(host)
logger.debug('Mongo connected.')
document_db = client.twitterdb

# Convert subject_list to string and underscores
col_name = '_'.join(k for k in subject_list if '#' not in k)

# Check if collection  name already exists
if col_name in document_db.collection_names():
    logger.debug('Collection {} exists'.format(col_name))
    collection = document_db[col_name]
else:
    document_db.create_collection(col_name)
    logger.debug('New collection {}'.format(col_name))
    collection = document_db[col_name]

print("Tweets will be stored in the MongoDB collection: {}".format(col_name))

# Set up tweepy credentials
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
logger.debug('Tweepy has loaded credentials.')

# Create listener based on tweepy Streamlistener
""" If used as streamer, max_limit and count will impact the
number of tweets collected.  However, as the connection is 
being broken for purpose of refreshing the tweet stream,
they are vestigial"""

class Listener(tweepy.StreamListener):
    def __init__(self, api, max_limit=1, timeout=sleep*5):
        #super(Listener, self).__init__()
        self.api = api
        self.count = 0
        self.limit = max_limit
        self.timeout = timeout

    def on_status(self, status):
        print('on_status')
        logger.debug(status.text)            

    def on_error(self, status_code):
        logger.debug(status_code)
        if status_code == 420:
            # Returning False disconnects the stream
            return False

    def on_timeout(self):#when times out in twitter- not runtime
        print('TIME OUT')
        return False
    
    def on_data(self, data):
        logger.debug('Pulling in tweets')
        while self.count < self.limit:
        # Insert into collection from above
            collection = document_db[col_name]
            tweet_json = json.loads(data)
            collection.insert_one(tweet_json)
            text = tweet_json['text']
            user = tweet_json['user']['screen_name']
            print(user,":", text)
            self.count += 1
        else:
            """Called when stream connection times out"""
            return False

    def _run(self):
         # Authenticate
         url = "https://%s%s" % (self.host, self.url)
 
         # Connect and process the stream
         error_counter = 0
         resp = None
         exception = None
         while self.running:
             if self.retry_count is not None:
                 if error_counter > self.retry_count:
                     # quit if error count greater than retry count
                     break
             try:
                 auth = self.auth.apply_auth()
                 resp = self.session.request('POST',
                                             url,
                                             data=self.body,
                                             timeout=self.timeout,
                                             stream=True,
                                             auth=auth,
                                             verify=self.verify)
                 if resp.status_code != 200:
                     if self.listener.on_error(resp.status_code) is False:
                         break
                     error_counter += 1
                     if resp.status_code == 420:
                         self.retry_time = max(self.retry_420_start,
                                               self.retry_time)
                     sleep(self.retry_time)
                     self.retry_time = min(self.retry_time * 2,
                                           self.retry_time_cap)
                 else:
                     error_counter = 0
                     self.retry_time = self.retry_time_start
                     self.snooze_time = self.snooze_time_step
                     self.listener.on_connect()
                     self._read_loop(resp)
             except (Timeout, ssl.SSLError, ConnectionError, ReadTimeoutError, ProtocolError) as exc:
                  # This is still necessary, as a SSLError can actually be
                  # thrown when using Requests
                  # If it's not time out treat it like any other exception
                 if isinstance(exc, ssl.SSLError):
                     if not (exc.args and 'timed out' in str(exc.args[0])):
                         exception = exc
                         break
                 if self.listener.on_timeout() is False:
                     break
                 if self.running is False:
                     break
                 sleep(self.snooze_time)
                 self.snooze_time = min(self.snooze_time + self.snooze_time_step,
                                        self.snooze_time_cap)
             except Exception as exc:
                 exception = exc
                 # any other exception is fatal, so kill loop
                 break

   
print('Storing the following tweets:')
for _ in range(num_tweets):
    streamer = tweepy.Stream(auth=auth, listener=Listener(api=tweepy.API(), timeout=sleep*5), running = True, timeout=sleep*5)
    print('I\'M LOOKING')
    streamer.filter(track=subject_list)
    time.sleep(sleep)

logger.debug('Done pulling in tweets.')
print('Done pulling in tweets.')
