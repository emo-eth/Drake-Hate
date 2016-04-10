#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import tweepy

# I created some test credentials using my account for the time 
# being. When we create our permanent ones, we should NOT push 
# code with credentials hardcoded to GitHub!
CONSUMER_KEY = 'FuFdD9Eoy1EyeXqRdYZWuPR04'
CONSUMER_SECRET = 'XUidcH5PwxRCuy4ljjWUy8orfCuZ5XBpzExiMDe2snISO71fWr'
ACCESS_KEY = '755491015-y1ntCjpOal2u4xwOKJ5xTeXNzutPv5WI9JZxIlk9'
ACCESS_SECRET = 'GJiEIx95eEbv5uCPepOZ0xSevzc1pjVJ3zpYqenil1gVl'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
