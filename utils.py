# Local Files
from user_blacklist import user_blacklist
from word_blacklist import word_blacklist

# Libraries
import sys
import os
import tweepy
import json

''' local vars '''

OBVIOUS_PHRASES = ['drake is trash', 'i hate drake']

TWITTER_SEARCH_LIMIT = 350
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''

# Store the ID of the last tweet we retweeted in a file
# so we don't retweet things twice!
bot_path = os.path.dirname(os.path.abspath(__file__))
last_id_file = os.path.join(bot_path, 'last_id')

''' helper fns'''


def dev_environ():
    ''' Boolean function that returns true if the dev flag is
        set on the command line and false otherwise.
    '''
    if len(sys.argv) > 1:
        if sys.argv[1] == '--dev':
            return True
    return False


def remove_quoted_text(twext):
    # alternate way of doing it?
    pieces = twext.split('"')
    # slice and skip by two
    cut_out_quotes = pieces[::2]
    temp = ''
    for piece in cut_out_quotes:
        temp += piece
    return temp


def load_oauth_keys(dev):
    if dev:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        CONSUMER_KEY = settings['CONSUMER_KEY']
        CONSUMER_SECRET = settings['CONSUMER_SECRET']
        ACCESS_KEY = settings['ACCESS_KEY']
        ACCESS_SECRET = settings['ACCESS_SECRET']
    else:
        CONSUMER_KEY = os.environ['CONSUMER_KEY']
        CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
        ACCESS_KEY = os.environ['ACCESS_KEY']
        ACCESS_SECRET = os.environ['ACCESS_SECRET']
    return True


def twitter_oauth(dev):
    ''' Handles Twitter OAuth and returns a Tweepy API object.
    '''
    load_oauth_keys(dev)
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    return tweepy.API(auth)


def load_savepoint():
    savepoint = ''
    try:
        with open(last_id_file, 'r') as file:
            savepoint = file.read()
    except IOError:
        print('No savepoint on file. Trying to download as many results as possible...')
    return savepoint


def write_savepoint(savepoint):
    with open(last_id_file, 'w') as file:
        file.write(str(savepoint))
    return True


def parse_savepoint_from_tweets(pre_clean_tweets):
    last_tweet = pre_clean_tweets[0]
    try:
        last_id = last_tweet.id
    except IndexError:
        last_id = ''
    return last_id

def twitter_search(api, savepoint):
    results = tweepy.Cursor(api.search, q='Drake', since_id=savepoint,
                            lang='en').items(TWITTER_SEARCH_LIMIT)
    tweets = []
    for tweet in results:
        tweets.append(tweet)
    return tweets


def clean_search_results(tweets):
    tweets = [tweet for tweet in tweets if not any(
        word.lower() in word_blacklist for word in tweet.text.split())]
    tweets = [tweet for tweet in tweets
              if tweet.author.screen_name not in user_blacklist]
    tweets.reverse()
    return tweets


def retweet(api, cleaned_tweets):
    retweets = 0
    for tweet in cleaned_tweets:
        twext = remove_quoted_text(tweet.text)
        for phrase in OBVIOUS_PHRASES:
            if phrase in twext.lower():
                api.retweet(tweet.id)
                retweets += 1
                print('Retweeting "%s"...' % twext)
    if retweets > 0:
        print('Retweeted %d haters' % retweets if retweets != 1 else 'Retweeted 1 hater')
    else:
        print('Nothing to retweet!')
    return retweets


def print_tweet_info(tweet):
    ''' Prints some basic info about the given tweet.
    '''
    print('(%s) %s: %s\n' % (tweet.created_at, tweet.author.screen_name, tweet.text))
