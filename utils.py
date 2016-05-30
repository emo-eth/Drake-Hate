# TODO: Move these functions back to the bot.py file. They are 
# temporarily living here until we set up a main method in the 
# bot.py file.

# Local files
from user_blacklist import user_blacklist
from word_blacklist import word_blacklist

# Libraries
import json
import sys
import os
import tweepy

def dev_environ():
    ''' Boolean function that returns true if the dev flag is
        set on the command line and false otherwise.
    '''
    if len(sys.argv) > 1:
        if sys.argv[1] == '--dev':
            return True

    return False


def twitter_oauth(dev):
    ''' Handles Twitter OAuth and returns a Tweepy API object.
    '''
    if dev:
        with open('settings.json', 'r') as f:
            settings = json.load(f)

        consumer_key = settings['CONSUMER_KEY']
        consumer_secret = settings['CONSUMER_SECRET']
        access_key = settings['ACCESS_KEY']
        access_secret = settings['ACCESS_SECRET']
    
    else:
        consumer_key = os.environ['CONSUMER_KEY']
        consumer_secret = os.environ['CONSUMER_SECRET']
        access_key = os.environ['ACCESS_KEY']
        access_secret = os.environ['ACCESS_SECRET']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    return tweepy.API(auth)


def remove_quoted_text(twext):
    ''' Removes all words within double quotes from the given string.
    '''
    result = ""
    in_quotes = False
    for c in twext:
        if c is '"':
            in_quotes = not in_quotes
            continue
        if not in_quotes:
            result = result + c
    
    # Quotations were mismatched! Return original string.
    if in_quotes is True:
        return twext
    
    return result


def contains_word_in_blacklist(tweet):
    words = [word.lower() for word in tweet.text.split()]
    return not set(words).isdisjoint(word_blacklist)


def contains_drake(tweet):
    words = [word.lower() for word in tweet.text.split()]
    return 'drake' in words


def blacklisted_author(tweet):
    return tweet.author.screen_name in user_blacklist


def clean_search_results(tweets):
    clean_tweets = []
    for tweet in tweets:
        if contains_word_in_blacklist(tweet):
            continue
        elif blacklisted_author(tweet):
            continue
        elif not contains_drake:
            continue
        else:
            clean_tweets.append(tweet)
    
    clean_tweets.reverse()
    return clean_tweets


def print_tweet_info(tweet):
    ''' Prints some basic info about the given tweet.
    '''
    print('(%s) %s: %s\n' % (tweet.created_at, tweet.author.screen_name, tweet.text))
