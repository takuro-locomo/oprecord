from sheets_service import get_service, spreadsheet_id
from chart_service import update_dashboard_data, create_dashboard_chart

def main():
    print("Setting up Analytics Dashboard...")
    client = get_service()
    if not client:
        print("Failed to get service client.")
        return

    # 1. Update Data first to ensure we have columns to chart
    print("Updating summary data...")
    sorted_years = update_dashboard_data(client, spreadsheet_id)
    
    if sorted_years:
        print(f"Found years: {sorted_years}")
        # 2. Create Chart
        print("Creating chart...")
        create_dashboard_chart(client, spreadsheet_id, sorted_years)
        print("Done!")
    else:
        print("No data found to chart.")

if __name__ == "__main__":
    main()
