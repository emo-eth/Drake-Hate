#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Partially adapted from flebel on GitHub at http://bit.ly/1ThAsJL.

# Local Files
import settings as settings
from user_blacklist import user_blacklist
from word_blacklist import word_blacklist

# Libraries
import os
import tweepy
import pickle
# from nltk.tokenize import word_tokenize

with open('sentim_analyzer.pk1', 'rb') as f:
    sentim_analyzer = pickle.load(f)

with open('classifier.pk1', 'rb') as f:
    classifier = pickle.load(f)

with open('trainer.pk1', 'rb') as f:
    trainer = pickle.load(f)


OBVIOUS_PHRASES = ['drake is trash', 'i hate drake']

TWITTER_SEARCH_LIMIT = 350

auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)
api = tweepy.API(auth)

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

# TODO: Handle emojis better! Right now tweet.text.split() is
# tokenizing tweets only at whitespace. It'd be nice to recognize
# a string of emojis and process them all individually, rather
# than as a collective 'word'.

# Filter tweets using blacklist
tweets = [tweet for tweet in tweets if not any(
    word.lower() in word_blacklist for word in tweet.text.split())]
tweets = [tweet for tweet in tweets
          if tweet.author.screen_name not in user_blacklist]
tweets.reverse()

for tweet in tweets:
    twext = tweet.text
    if 'drake is trash' in twext.lower():
        api.retweet(tweet.id)


# Write last retweeted tweet id to file
with open(last_id_file, 'w') as file:
    file.write(str(last_tweet_id))
