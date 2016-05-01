#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Partially adapted from flebel on GitHub at http://bit.ly/1ThAsJL.

# API Keys
import settings as settings
import os
import tweepy
import inspect
import hashlib
import pickle
from nltk.tokenize import word_tokenize

with open('sentim_analyzer.pk1', 'rb') as f:
    sentim_analyzer = pickle.load(f)

with open('classifier.pk1', 'rb') as f:
    classifier = pickle.load(f)

with open('trainer.pk1', 'rb') as f:
    trainer = pickle.load(f)

TWITTER_SEARCH_LIMIT = 350

auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)
api = tweepy.API(auth)

# Load blacklists from file
# TODO: This is clunky af! Can I make it more Pythonic? Maybe move to
# helper fn?
with open('word_blacklist.txt', 'r', encoding='utf-8') as f:
    word_blacklist = [word.strip().lower() for word in f.readlines()
                      if word and not word.startswith('# ')]


with open("user_blacklist.txt", 'r', encoding='utf-8') as f:
    user_blacklist = [user.strip() for user in f.readlines()
                      if user != '' and user[0] != '#']

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


for i in range(len(tweets)):
    tweet = tweets[i].text
    print(sentim_analyzer.classify(word_tokenize(tweet)))
    print('(%s) %s: %s\n' %
          (tweets[i].created_at,
           tweets[i].author.screen_name.encode('utf-8'),
           tweet))

# Write last retweeted tweet id to file
# with open(last_id_file, 'w') as file:
#     file.write(str(last_tweet_id))
