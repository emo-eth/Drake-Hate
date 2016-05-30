# Local Files
from user_blacklist import user_blacklist
from word_blacklist import word_blacklist

# Libraries
import sys
import os
import tweepy
import json
from gspread_utils import *

'''Global vars'''


def dev_environ():
    ''' Boolean function that returns true if the dev flag is
        set on the command line and false otherwise.
    '''
    if len(sys.argv) > 1:
        if sys.argv[1] == '--dev':
            return True
    return False

OBVIOUS_PHRASES = ['drake is trash', 'i hate drake']

TWITTER_SEARCH_LIMIT = 350
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''
API = None

dev = dev_environ()
gapi = gspread_oauth(dev)

wks = gapi.open_by_key(SPREADSHEET_KEY).sheet1
NUM_TWEETS_LOGGED = len(wks.get_all_values())

''' helper fns'''


def remove_quoted_text(twext):
    # alternate way of doing it?
    pieces = twext.split('"')
    # slice and skip by two
    cut_out_quotes = pieces[::2]
    temp = ''
    for piece in cut_out_quotes:
        temp += piece
    return temp


def load_oauth_keys():
    global CONSUMER_KEY
    global CONSUMER_SECRET
    global ACCESS_KEY
    global ACCESS_SECRET
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        CONSUMER_KEY = settings['CONSUMER_KEY']
        CONSUMER_SECRET = settings['CONSUMER_SECRET']
        ACCESS_KEY = settings['ACCESS_KEY']
        ACCESS_SECRET = settings['ACCESS_SECRET']
    except:
        CONSUMER_KEY = os.environ['CONSUMER_KEY']
        CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
        ACCESS_KEY = os.environ['ACCESS_KEY']
        ACCESS_SECRET = os.environ['ACCESS_SECRET']
    return True


def twitter_oauth():
    ''' Handles Twitter OAuth and returns a Tweepy API object.
    '''
    load_oauth_keys()
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
        print('error')
        last_id = ''
    return last_id


def twitter_search(api, savepoint):
    results = tweepy.Cursor(api.search, q='Drake', savepoint=savepoint,
                            lang='en').items(TWITTER_SEARCH_LIMIT)
    tweets = []
    for tweet in results:
        tweets.append(tweet)
    return tweets


def retweet(api, cleaned_tweets):
    global NUM_TWEETS_LOGGED
    num_retweets = 0
    for tweet in cleaned_tweets:
        if NUM_TWEETS_LOGGED < MAX_NUM_TWEETS:
            NUM_TWEETS_LOGGED = add_to_spreadsheet(wks, NUM_TWEETS_LOGGED, tweet)
        twext = remove_quoted_text(tweet.text)
        for phrase in OBVIOUS_PHRASES:
            if phrase in twext.lower():
                api.retweet(tweet.id)
                num_retweets += 1
                print('Retweeting "%s"...' % twext)
        # Testing/ debug stuff
        if dev:
            print_tweet_info(tweet)
    if num_retweets > 0:
        print('Retweeted %d haters' % num_retweets if num_retweets != 1 else 'Retweeted 1 hater')
    else:
        print('Nothing to retweet!')
        num_retweets = -1
    return num_retweets


def print_tweet_info(tweet):
    ''' Prints some basic info about the given tweet.
    '''
    print('(%s) %s: %s\n' % (tweet.created_at, tweet.author.screen_name, tweet.text))


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

''' local vars '''

# Store the ID of the last tweet we retweeted in a file
# so we don't retweet th
bot_path = os.path.dirname(os.path.abspath(__file__))
last_id_file = os.path.join(bot_path, 'last_id')


if __name__ == "__main__":
    dev = True
    load_oauth_keys(dev)
    API = twitter_oauth(dev)
    savepoint = load_savepoint()
    tweets = twitter_search(savepoint)
    savepoint = parse_savepoint_from_tweets(tweets)
    tweets = clean_search_results(tweets)
    retweet(tweets)
    write_savepoint(savepoint)
