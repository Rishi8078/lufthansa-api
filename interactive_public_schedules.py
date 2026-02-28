import sys
import json
from datetime import datetime
from luftansa-api.lufthansa_api import LufthansaAPIClient

def print_results(items):
    if not items:
        print("No flight schedules found.")
        return
        
    if isinstance(items, dict):
        items = [items]
        
    print(f"\n--- Public Flight Schedules ({len(items)} results) ---")
    for item in items:
        airline = item.get('airline', 'N/A')
        flight_num = item.get('flightNumber', 'N/A')
        
        # Determine Period
        period = item.get('periodOfOperationUTC', {})
        start_date = period.get('startDate', 'N/A')
        end_date = period.get('endDate', 'N/A')
        days = period.get('daysOfOperation', '').strip()
        
        print(f"\n[{airline} {flight_num}] Period: {start_date} to {end_date} | Days: {days}")
        
        # Legs
        legs = item.get('legs', [])
        for leg in legs:
            seq = leg.get('sequenceNumber', '?')
            origin = leg.get('origin', 'N/A')
            dest = leg.get('destination', 'N/A')
            ac_type = leg.get('aircraftType', 'N/A')
            dept_time = leg.get('aircraftDepartureTimeUTC', 'N/A')
            arr_time = leg.get('aircraftArrivalTimeUTC', 'N/A')
            
            # Times are in minutes from midnight UTC according to example
            dept_str = f"{dept_time // 60:02d}:{dept_time % 60:02d} UTC" if isinstance(dept_time, int) else dept_time
            arr_str = f"{arr_time // 60:02d}:{arr_time % 60:02d} UTC" if isinstance(arr_time, int) else arr_time
            
            print(f"  Leg {seq}: {origin} ({dept_str}) -> {dest} ({arr_str}) | Aircraft: {ac_type}")

def format_date(date_str):
    """
    Tries to parse various date formats and return the strict DDMMMYY format needed by the API.
    Handles inputs like: '04MAR2026', '2026-03-04', '04/03/2026', '04MAR26', etc.
    If parsing fails, simply returns the stripped, uppercase string and lets the API handle the error.
    """
    date_str = date_str.strip().upper()
    formats = [
        "%d%b%Y", # 04MAR2026
        "%Y-%m-%d", # 2026-03-04
        "%d/%m/%Y", # 04/03/2026
        "%d-%m-%Y", # 04-03-2026
        "%d%b%y", # 04MAR26 (already correct)
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%d%b%y").upper()
        except ValueError:
            continue
            
    # Remove leading parenthesis or other accidental typos if we still couldn't parse it
    # Just in case the user typed ')04MAR2026' as seen in the logs
    for char in ['(', ')', '!', '@', '#', '$', '%']:
        date_str = date_str.replace(char, '')
        
    # Try one more time after basic cleaning just for the 04MAR2026 structure issue seen in log
    try:
         dt = datetime.strptime(date_str, "%d%b%Y")
         return dt.strftime("%d%b%y").upper()
    except ValueError:
         pass

    return date_str

def main():
    print("Initializing Lufthansa API Client...")
    try:
        api = LufthansaAPIClient()
        api.authenticate()
        print("Authentication successful!")
    except Exception as e:
        print(f"Authentication failed: {e}")
        print("Please check your .env file credentials.")
        sys.exit(1)

    while True:
        print("\n=== Lufthansa API: Public Flight Schedules ===")
        print("Enter search parameters (press Enter to skip optional fields).")
        print("Type 'exit' or 'quit' in any field to stop.\n")
        
        airlines = input("Airlines (e.g. LH, or multiple like LH,LX) [*REQUIRED]: ").strip().upper()
        if airlines.lower() in ['exit', 'quit']: break
        
        flight_number_ranges = input("Flight Number Ranges (e.g. 400-405) [Optional]: ").strip()
        if flight_number_ranges.lower() in ['exit', 'quit']: break
        
        start_date = input("Start Date (e.g. 05DEC19) [*REQUIRED]: ").strip().upper()
        if start_date.lower() in ['exit', 'quit']: break
        start_date = format_date(start_date)
        
        end_date = input("End Date (e.g. 10DEC19) [*REQUIRED]: ").strip().upper()
        if end_date.lower() in ['exit', 'quit']: break
        end_date = format_date(end_date)
        
        days_of_operation = input("Days of Operation (1=Mon...7=Sun, e.g. 1234567) [Leave blank for all days]: ").strip()
        if days_of_operation.lower() in ['exit', 'quit']: break
        if not days_of_operation:
            days_of_operation = "1234567"
        
        if not airlines or not start_date or not end_date:
            print("\nError: Airlines, Start Date, and End Date are strictly required for this search.")
            continue
            
        try:
            print("\nFetching public schedules...")
            res = api.get_public_flight_schedules(
                airlines=airlines,
                flight_number_ranges=flight_number_ranges if flight_number_ranges else None,
                start_date=start_date,
                end_date=end_date,
                days_of_operation=days_of_operation
            )
            
            # The API returns a list directly according to the docs
            print_results(res)
            
        except Exception as e:
            print(f"\nAPI Error: {e}")

if __name__ == "__main__":
    main()
