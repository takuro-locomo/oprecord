import gspread
from collections import defaultdict
from datetime import datetime

def update_dashboard_data(client, spreadsheet_id):
    try:
        sheet = client.open_by_key(spreadsheet_id).sheet1
        
        # 1. Fetch Dates (Column F)
        dates = sheet.col_values(6)[1:] # Column F is index 6
        
        # 2. Aggregate Data
        counts = defaultdict(lambda: defaultdict(int))
        years = set()
        
        for date_str in dates:
            if not date_str:
                continue
            try:
                dt = datetime.strptime(date_str, "%Y/%m/%d")
                counts[dt.year][dt.month] += 1
                years.add(dt.year)
            except ValueError:
                continue
                
        sorted_years = sorted(list(years))
        
        # 3. Prepare Summary Table Data
        header = ["Month"] + [str(y) for y in sorted_years]
        
        table_data = [header]
        for month in range(1, 13):
            row = [month]
            for year in sorted_years:
                row.append(counts[year][month])
            table_data.append(row)
            
        # 4. Write Table to Sheet (Starting at Column W -> Index 23)
        start_col_char = 'W'
        # Simple char math for column letters (Works for A-Z, AA-AZ etc logic needed if many years)
        # For now assuming years < 4 (W, X, Y, Z)
        
        range_name = f"W1" # Start cell
        
        sheet.update(range_name=range_name, values=table_data)
        print(f"Updated summary table at {range_name}")
        return sorted_years
        
    except Exception as e:
        print(f"Dashboard Data Error: {e}")
        return []

def create_dashboard_chart(client, spreadsheet_id, sorted_years):
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        sheet = spreadsheet.sheet1
        sheet_id = sheet.id
        
        # Define Chart Spec
        domain_source = {
            "sheetId": sheet_id,
            "startRowIndex": 0, # Row 1 (Header + Data)
            "endRowIndex": 13,  # Row 13
            "startColumnIndex": 22, # W
            "endColumnIndex": 23
        }
        
        # Color Palette (RGB 0-1)
        # 2023: Blue, 2024: Red/Orange, 2025: Green
        colors = {
            2023: {"red": 0.25, "green": 0.5, "blue": 0.9}, # Blue
            2024: {"red": 0.9, "green": 0.4, "blue": 0.2},  # Orange/Red
            2025: {"red": 0.2, "green": 0.7, "blue": 0.3},  # Green
            2026: {"red": 0.6, "green": 0.2, "blue": 0.8},  # Purple
        }
        
        series_list = []
        for i, year in enumerate(sorted_years):
            col_idx = 23 + i # X, Y...
            
            # Default to Gray if year not in palette
            color = colors.get(year, {"red": 0.5, "green": 0.5, "blue": 0.5})
            
            series_list.append({
                "series": {
                    "sourceRange": {
                        "sources": [{
                            "sheetId": sheet_id,
                            "startRowIndex": 0, # Row 1 (Header + Data)
                            "endRowIndex": 13,
                            "startColumnIndex": col_idx,
                            "endColumnIndex": col_idx + 1
                        }]
                    }
                },
                "targetAxis": "LEFT_AXIS",
                "dataLabel": {
                    "type": "DATA"
                },
                "color": color
            })

        chart_spec = {
            "title": "Monthly Case Counts by Year",
            "basicChart": {
                "chartType": "LINE",
                "legendPosition": "RIGHT_LEGEND",
                "axis": [
                    {"position": "BOTTOM_AXIS", "title": "Month"},
                    {"position": "LEFT_AXIS", "title": "Number of Cases"}
                ],
                "domains": [{
                    "domain": {
                        "sourceRange": {
                            "sources": [domain_source]
                        }
                    }
                }],
                "series": series_list,
                "headerCount": 1 # Use first row as headers
            }
        }
        
        requests = [{
            "addChart": {
                "chart": {
                    "spec": chart_spec,
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": sheet_id,
                                "rowIndex": 0,
                                "columnIndex": 23 + len(sorted_years) + 1
                            },
                            "widthPixels": 600,
                            "heightPixels": 400
                        }
                    }
                }
            }
        }]
        
        spreadsheet.batch_update({"requests": requests})
        print("Created dashboard chart")
        return True
    except Exception as e:
        print(f"Chart Creation Error: {e}")
        return False
