import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
from chart_service import update_dashboard_data

load_dotenv()

# Setup Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
spreadsheet_id = os.getenv("SPREADSHEET_ID")

def get_service():
    if not os.path.exists(creds_file):
        print("Credentials file not found.")
        return None
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)
    return client

def save_to_sheet(data):
    client = get_service()
    if not client:
        return False
    
    try:
        sheet = client.open_by_key(spreadsheet_id).sheet1
        
        # 1. Determine the next row index based on Column E (ID) which should always be present
        existing_ids = sheet.col_values(5) # Column E is index 5 (1-based)
        next_row_index = len(existing_ids) + 1
        
        # 2. Auto-calculate 'total number' (Column D) and 'anual number' (Column C)
        existing_totals = sheet.col_values(4) # Column D is index 4
        existing_anuals = sheet.col_values(3) # Column C is index 3
        
        next_total_number = 1
        next_anual_number = 1
        
        # Helper to find last number
        def get_last_number(values):
            if len(values) > 1:
                last_val = values[-1]
                if not str(last_val).isdigit():
                    for val in reversed(values):
                        if str(val).isdigit():
                            return int(val)
                elif str(last_val).isdigit():
                    return int(last_val)
            return 0

        last_total = get_last_number(existing_totals)
        if last_total > 0:
            next_total_number = last_total + 1
            
        last_anual = get_last_number(existing_anuals)
        if last_anual > 0:
            next_anual_number = last_anual + 1
            
        # 3. Construct the row data
        row_values = [
            "",                      # A
            data.get("comment", ""), # B
            next_anual_number,       # C
            next_total_number,       # D
            data.get("id", ""),      # E
            data.get("date", ""),    # F
            "",                      # G
            data.get("sex", ""),     # H
            1,                       # I (Primary - Default to 1)
            data.get("age", ""),     # J
            data.get("side", ""),    # K
            data.get("diagnosis", ""), # L
            data.get("cement", ""),  # M
            data.get("stem", ""),    # N
            data.get("mdm", ""),     # O
            data.get("cup", ""),     # P
            data.get("screw", ""),   # Q
            data.get("head", ""),    # R
            "",                      # S
            data.get("time", ""),    # T
            data.get("bleeding", "") # U
        ]
        
        # 4. Write to the specific range
        range_name = f"A{next_row_index}:U{next_row_index}"
        
        print(f"Writing to range {range_name}: {row_values}")
        sheet.update(range_name=range_name, values=[row_values])
        
        # 5. Update Dashboard Data (Chart Source)
        print("Updating dashboard data...")
        update_dashboard_data(client, spreadsheet_id)
        
        return True
    except Exception as e:
        print(f"Sheets Error: {e}")
        raise Exception(f"Failed to save to Google Sheets: {e}")
