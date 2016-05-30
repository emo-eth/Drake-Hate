#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Partially adapted from flebel on GitHub at http://bit.ly/1ThAsJL.

# Local Files
from utils import *
from gspread_utils import *

OBVIOUS_PHRASES = ['drake is trash', 'i hate drake']
TWITTER_SEARCH_LIMIT = 350

dev = dev_environ()
api = twitter_oauth(dev)
gapi = gspread_oauth(dev)

wks = gapi.open_by_key(SPREADSHEET_KEY).sheet1
num_tweets_logged = len(wks.get_all_values())

# Store the ID of the last tweet we retweeted in a file
# so we don't retweet things twice!
bot_path = os.path.dirname(os.path.abspath(__file__))
last_id_file = os.path.join(bot_path, 'last_id')

savepoint = ''
try:
    with open(last_id_file, 'r') as file:
        savepoint = file.read()
except IOError:
    print('No savepoint on file. Trying to download as many results as possible...')

results = tweepy.Cursor(api.search, q='Drake', since_id=savepoint, lang='en').items(TWITTER_SEARCH_LIMIT)

# Put all of the tweets into a list so we can filter them
tweets = []
for tweet in results:
    tweets.append(tweet)
try:
    last_tweet_id = tweets[0].id
except IndexError:  # No results found
    last_tweet_id = savepoint

tweets = clean_search_results(tweets)

retweets = 0

for tweet in tweets:
    if num_tweets_logged < MAX_NUM_TWEETS:
        num_tweets_logged = add_to_spreadsheet(wks, num_tweets_logged, tweet)

    twext = remove_quoted_text(tweet.text)
    for phrase in OBVIOUS_PHRASES:
        if phrase in twext.lower():
            api.retweet(tweet.id)
            retweets += 1
            print('Retweeting "%s"...' % twext)

    # Testing/ debug stuff
    if dev:
        print_tweet_info(tweet)

if retweets > 0:
    print('Retweeted %d haters' % retweets if retweets != 1 else 'Retweeted 1 hater')
else:
    print('Nothing to retweet!')

# Write last retweeted tweet id to file
with open(last_id_file, 'w') as file:
    file.write(str(last_tweet_id))
