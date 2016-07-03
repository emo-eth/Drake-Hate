import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import crypt

SPREADSHEET_KEY = '1hUA03o4uOQvcywtIzlfUsP_DbDzwdShNlpsGecWSOME'
NUM_ROWS_TO_ADD = 1000
MAX_NUM_TWEETS = 10000


def get_gspread_credentials():
    ''' Returns a Google Spreadsheets credentials object.
    '''
    try:
        with open('gspread_settings.json', 'r') as f:
            settings = json.load(f)

        service_account_email = settings['client_email']
        private_key_pkcs8_pem = settings['private_key']
        private_key_id = settings['private_key_id']
        client_id = settings['client_id']
    except:
        service_account_email = os.environ['GSPREAD_CLIENT_EMAIL']
        private_key_pkcs8_pem = os.environ['GSPREAD_PRIVATE_KEY']
        private_key_id = os.environ['GSPREAD_PRIVATE_KEY_ID']
        client_id = os.environ['GSPREAD_CLIENT_ID']

    signer = crypt.Signer.from_string(private_key_pkcs8_pem)
    credentials = ServiceAccountCredentials(service_account_email, signer,
                                            scopes='https://spreadsheets.google.com/feeds', 
                                            private_key_id=private_key_id, client_id=client_id)
    credentials._private_key_pkcs8_pem = private_key_pkcs8_pem

    return credentials


def gspread_oauth():
    ''' Returns a Gspread Client instance.
    '''
    credentials = get_gspread_credentials()
    return gspread.authorize(credentials)


def _duplicate_tweet(wks, text):
    try:
        wks.find(text)
    except gspread.CellNotFound:
        return False
    return True


def add_to_spreadsheet(wks, num_tweets, tweet):
    ''' Adds the text from the Tweet object to the Google Sheet.
        Returns the total number of tweets now logged on the spreadsheet.
    '''
    text = tweet.text

    if _duplicate_tweet(wks, text): return

    if num_tweets + 1 > wks.row_count:
        wks.add_rows(NUM_ROWS_TO_ADD)

    # WATCH OUT: ROWS AND COLUMNS ARE NOT ZERO INDEXED!
    wks.update_cell(num_tweets + 1, 1, text)
    return num_tweets + 1
