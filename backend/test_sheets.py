import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Define the scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Load credentials
creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
spreadsheet_id = os.getenv("SPREADSHEET_ID")

print(f"Credentials file: {creds_file}")
print(f"Spreadsheet ID: {spreadsheet_id}")

try:
    if not os.path.exists(creds_file):
        print("Error: credentials.json not found!")
        exit(1)
        
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)
    
    print("Successfully authorized.")
    
    print(f"Opening spreadsheet with ID: {spreadsheet_id}")
    sheet = client.open_by_key(spreadsheet_id).sheet1
    
    print("Successfully opened sheet.")
    print(f"Sheet title: {sheet.title}")
    
    # Try appending a test row
    print("Attempting to append a test row...")
    sheet.append_row(["Test", "Row", "From", "Script"])
    print("Successfully appended row.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
