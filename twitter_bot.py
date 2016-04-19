#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# API Keys
import settings as settings
import os, tweepy, inspect, hashlib

TWITTER_SEARCH_LIMIT = 350

auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)
api = tweepy.API(auth)

# Very incomplete list of music/ media blogs. Exclude tweets from 
# these accounts, because we can assume they won't be tweeting hate!
# TODO: Move this to a separate file or something?
user_blacklist = ['billboard', 'pitchfork', 'ComplexMusic', 'PigsAndPlans', 'stereogum', \
                  'ComplexMag', 'thefader', 'RapDirect', 'NoiseyMusic', 'Beats1', 'XXL', \
                  'NME', 'MTVNews', 'SCENE', 'BleacherReport', 'SPINmagazine', 'iHeartRadio', \
                  'boilerroomtv', 'BLUNTIQ', 'AppleMusic', 'SaintHeron', 'chartnews', 'i_D']
word_blacklist = ['RT', u'♺']

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

results = tweepy.Cursor(api.search, q='@Drake', since_id=savepoint, lang='en').items(TWITTER_SEARCH_LIMIT)

# Put all of the tweets into a list so we can filter them
tweets = []
for tweet in results:
    tweets.append(tweet)

try:
    last_tweet_id = tweets[0].id
except IndexError: # No results found
    last_tweet_id = savepoint

# Filter tweets using blacklist
tweets = [tweet for tweet in tweets if not any(word in tweet.text.split() for word in word_blacklist)]
tweets = [tweet for tweet in tweets if tweet.author.screen_name not in user_blacklist]
tweets.reverse()

for i in range(len(tweets)):
    print('(%s) %s: %s\n' % \
            (tweets[i].created_at,
             tweets[i].author.screen_name.encode('utf-8'),
             tweets[i].text.encode('utf-8')))

# Write last retweeted tweet id to file
# with open(last_id_file, 'w') as file:
#     file.write(str(last_tweet_id))
