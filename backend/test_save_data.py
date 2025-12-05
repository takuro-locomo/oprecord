from sheets_service import save_to_sheet
import json

# Mock data similar to what frontend sends
mock_data = {
    "id": "12345678",
    "date": "2025/01/01",
    "sex": 1,
    "age": 75,
    "side": 1,
    "diagnosis": 1,
    "cement": None, # Test None value
    "stem": "Test Stem",
    "mdm": 0,
    "cup": "52",
    "screw": "2",
    "head": "32",
    "time": 90,
    "bleeding": 50,
    "comment": "Test Comment"
}

print("Testing save_to_sheet with mock data...")
try:
    save_to_sheet(mock_data)
    print("Successfully saved data.")
except Exception as e:
    print(f"Failed to save data: {e}")
    import traceback
    traceback.print_exc()
