import gspread
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import crypt

def get_gspread_credentials(dev):
    ''' Returns a Google Spreadsheets credentials object.
    '''
    if dev:
        with open('gspread_settings.json', 'r') as f:
            settings = json.load(f)

        service_account_email = settings['client_email']
        private_key_pkcs8_pem = settings['private_key']
        private_key_id = settings['private_key_id']
        client_id = settings['client_id']
    
    else:
        service_account_email = os.environ['GSPREAD_CLIENT_EMAIL']
        private_key_pkcs8_pem = os.environ['GSPREAD_PRIVATE_KEY']
        private_key_id = os.environ['GSPREAD_PRIVATE_KEY_ID']
        client_id = os.environ['GSPREAD_CLIENT_ID']

    signer = crypt.Signer.from_string(private_key_pkcs8_pem)
    credentials = ServiceAccountCredentials(service_account_email, signer, scopes='https://spreadsheets.google.com/feeds', private_key_id=private_key_id, client_id=client_id)
    credentials._private_key_pkcs8_pem = private_key_pkcs8_pem

    return credentials
