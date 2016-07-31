# Local Files
from blacklists import user_blacklist, word_blacklist

# Libraries
import sys
import os
import tweepy
import json
from gspread_utils import *

# Globals

OBVIOUS_PHRASES = ['drake is trash', 'i hate drake']
RETWEET_KEYWORDS = ['overrated', 'poor drake', 'trash', 'garbage', 'unpopular opinion'
                    'hate drake', 'fuck drake', 'murdered drake', "don't @ me", 'dont @ me',
                    "don't mention me", 'dont mention me', 'irrelevant', 'annoy', 'fraud',
                    'ghost', 'sucked', 'wheelchair', 'no offense', ' fat ', 'ugly',
                    'drake sucks', 'stfu drake']
DRAKE_NAMES = ['drake', '@drake', 'drizzy']
TWITTER_SEARCH_LIMIT = 350

num_tweets_logged = None

# Helper functions

def remove_quoted_text(twext):
    # alternate way of doing it?
    pieces = twext.split('"')
    # slice and skip by two
    cut_out_quotes = pieces[::2]
    temp = ''
    for piece in cut_out_quotes:
        temp += piece
    return temp


def read_from_local_file(keys):
    with open('settings.json', 'r') as f:
        settings = json.load(f)
    keys['consumer_key'] = settings['CONSUMER_KEY']
    keys['consumer_secret'] = settings['CONSUMER_SECRET']
    keys['access_key'] = settings['ACCESS_KEY']
    keys['access_secret'] = settings['ACCESS_SECRET']
    return keys


def read_from_heroku(keys):
    keys['consumer_key'] = os.environ['CONSUMER_KEY']
    keys['consumer_secret'] = os.environ['CONSUMER_SECRET']
    keys['access_key'] = os.environ['ACCESS_KEY']
    keys['access_secret'] = os.environ['ACCESS_SECRET']
    return keys


def load_oauth_keys():
    keys = {}
    try:
        keys = read_from_local_file(keys)
    except FileNotFoundError:
        keys = read_from_heroku(keys)
    return keys


def twitter_oauth():
    '''Handles Twitter OAuth and returns a Tweepy API object.'''
    keys = load_oauth_keys()
    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_key'], keys['access_secret'])
    return tweepy.API(auth)


def print_tweet_info(tweet):
    '''Prints some basic info about the given tweet to stdout.'''
    print('(%s) %s: %s\n' % (tweet.created_at, tweet.author.screen_name, tweet.text))


def retweet(dev, api, wks, tweets):
    global num_tweets_logged

    num_retweets = 0
    for tweet in tweets:
        if any(keyword in tweet.text.lower() for keyword in RETWEET_KEYWORDS) and num_tweets_logged < MAX_NUM_TWEETS:
            print('Adding "{0}" to spreadsheet...\n'.format(tweet.text))
            num_tweets_logged = add_to_spreadsheet(wks, num_tweets_logged, tweet)

        for phrase in OBVIOUS_PHRASES:
            if phrase in tweet.text.lower():
                api.retweet(tweet.id)
                num_retweets += 1
                print('Retweeting {0}...\n'.format(tweet.text))

        # Testing/ debug stuff
        if dev: print_tweet_info(tweet)
    return num_retweets


def contains_word_in_blacklist(tweet):
    words = [word.lower() for word in tweet.text.split()]
    return any(word in words for word in word_blacklist)


def contains_drake(tweet):
    words = [word.lower() for word in tweet.text.split()]
    return any(name in words for name in DRAKE_NAMES)


def blacklisted_author(tweet):
    return tweet.author.screen_name in user_blacklist


def filter_tweets(tweets):
    clean_tweets = []
    for tweet in tweets:
        if contains_word_in_blacklist(tweet):
            continue
        if blacklisted_author(tweet):
            continue
        if not contains_drake(tweet):
            continue
        tweet.text = remove_quoted_text(tweet.text)
        if tweet.text.strip():
            clean_tweets.append(tweet)

    clean_tweets.reverse()
    return clean_tweets


def twitter_search(api):
    results = tweepy.Cursor(api.search, q='Drake', lang='en').items(TWITTER_SEARCH_LIMIT)
    tweets = []
    for tweet in results:
        tweets.append(tweet)
    return tweets


def get_tweets(api):
    tweets = twitter_search(api)
    return filter_tweets(tweets)


def open_spreadsheet():
    gapi = gspread_oauth()
    return gapi.open_by_key(SPREADSHEET_KEY).sheet1


def dev_environ(argv):
    '''Returns true if the dev flag is set on the command line. False otherwise.'''
    if len(argv) > 1:
        if argv[1] == '--dev':
            return True
    return False


def main(argv=sys.argv):
    global num_tweets_logged

    dev = dev_environ(argv)
    api = twitter_oauth()

    wks = open_spreadsheet()
    num_tweets_logged = len(wks.get_all_values())

    tweets = get_tweets(api)
    num_retweets = retweet(dev, api, wks, tweets)

    if num_retweets > 0:
        print('Retweeted %d haters' % num_retweets if num_retweets != 1 else 'Retweeted 1 hater')
    else:
        print('Nothing to retweet!')


if __name__ == "__main__":
    main()
