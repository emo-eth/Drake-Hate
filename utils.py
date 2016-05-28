# TODO: Move these functions back to the bot.py file. They are 
# temporarily living here until we set up a main method in the 
# bot.py file.

# Libraries
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

# def dev_oauth():

def prod_oauth():
    auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
    auth.set_access_token(os.environ['ACCESS_KEY'], os.environ['ACCESS_SECRET'])
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

