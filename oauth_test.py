import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']

credentials = ServiceAccountCredentials.from_json_keyfile_name('gspread-creds.json', scope)

gc = gspread.authorize(credentials)

wks = gc.open_by_key('1O3BA6LEaoZgz8LVbsns8PKcJwbrd3lASnRx4ijV6F1o').sheet1

# Use this to find out how many tweets we already have on the spreadsheet
num_populated_rows = len(wks.get_all_values())

# WATCH OUT: ROWS AND COLUMNS ARE NOT ZERO INDEXED!
wks.update_cell(num_populated_rows + 1, 1, 'New tweet!') 
