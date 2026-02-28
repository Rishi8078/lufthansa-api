import sys
import json
from datetime import datetime
from luftansa-api.lufthansa_api import LufthansaAPIClient

def format_date(date_str):
    """Parses date to strictly YYYY-MM-DD format as required by Offers API."""
    date_str = date_str.strip().upper()
    formats = [
        "%Y-%m-%d", "%d%b%Y", "%d/%m/%Y", "%d-%m-%Y", "%d%b%y"
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str

def print_seat_map(data):
    if not data:
        print("No seat map data found.")
        return
        
    try:
        flights = data.get("Flight", [])
        if isinstance(flights, dict):
            flights = [flights]
            
        for f in flights:
            dept = f.get('Departure', {}).get('AirportCode', 'N/A')
            arr = f.get('Arrival', {}).get('AirportCode', 'N/A')
            mc = f.get('MarketingCarrier', {})
            flight_num = f"{mc.get('AirlineID', '')} {mc.get('FlightNumber', '')}"
            eq = f.get('Equipment', {}).get('AircraftCode', 'N/A')
            print(f"\n[Flight {flight_num}] {dept} -> {arr} | Equipment: {eq}")
    except Exception as e:
        print("Could not parse Flight header.")

    # Seat Details
    seat_details = data.get("SeatDetails", [])
    if isinstance(seat_details, dict):
        seat_details = [seat_details]
        
    print(f"\n--- Total Seats Parsed: {len(seat_details)} ---")
    
    # Just print the first 15 for brevity, otherwise console gets flooded
    for seat in seat_details[:15]:
        loc = seat.get('Location', {})
        col = loc.get('Column', '?')
        row_dict = loc.get('Row', {})
        row = row_dict.get('Number', '?')
        
        chars = row_dict.get('Characteristics', {}).get('Characteristic', [])
        if isinstance(chars, dict):
            chars = [chars]
        
        char_codes = [c.get('Code', '') for c in chars if 'Code' in c]
        print(f"  Seat {row}{col} | Characteristics: {','.join(char_codes)}")

    if len(seat_details) > 15:
        print(f"  ... and {len(seat_details) - 15} more seats.")

def print_lounges(data):
    if not data:
        print("No lounge data found.")
        return
        
    if isinstance(data, dict) and "Lounge" in data:
        lounges = data["Lounge"]
    else:
        lounges = data
        
    if isinstance(lounges, dict):
        lounges = [lounges]
        
    print(f"\n--- Lounges ({len(lounges)} results) ---")
    for lounge in lounges:
        names = lounge.get('Names', {}).get('Name', [])
        if isinstance(names, dict): names = [names]
        
        lounge_name = next((n['$'] for n in names if isinstance(n, dict) and n.get('@LanguageCode') == 'en'), "Unknown Lounge")
        if lounge_name == "Unknown Lounge" and names:
            lounge_name = names[0].get('$', "Unknown Lounge") if isinstance(names[0], dict) else str(names[0])
            
        # For XML converted to dict, text values are often under '$' key
        if isinstance(lounge_name, dict) and '$' in lounge_name:
            lounge_name = lounge_name['$']

        ap_code = lounge.get('AirportCode', 'N/A')
        if isinstance(ap_code, dict) and '$' in ap_code: ap_code = ap_code['$']
            
        print(f"\n[{ap_code}] {lounge_name}")
        
        locations = lounge.get('Locations', {}).get('Location', [])
        if isinstance(locations, dict): locations = [locations]
        
        loc_desc = next((l['$'] for l in locations if isinstance(l, dict) and l.get('@LanguageCode') == 'en'), "")
        if loc_desc:
             # handle possible nested dictionaries from xml to json
             if isinstance(loc_desc, dict) and '$' in loc_desc: loc_desc = loc_desc['$']
             print(f"  Location: {loc_desc}")
             
        hours = lounge.get('OpeningHours', {}).get('OpeningHours', [])
        if isinstance(hours, dict): hours = [hours]
        
        hour_desc = next((h['$'] for h in hours if isinstance(h, dict) and h.get('@LanguageCode') == 'en'), "")
        if hour_desc:
             # handle possible nested dictionaries from xml to json
             if isinstance(hour_desc, dict) and '$' in hour_desc: hour_desc = hour_desc['$']
             print(f"  Hours: {hour_desc}")
             
        # Extract some boolean features
        feats = lounge.get('Features', {})
        active_feats = []
        for feat, val in feats.items():
            if isinstance(val, dict) and val.get('$') == 'true':
                 active_feats.append(feat)
            elif str(val).lower() == 'true':
                 active_feats.append(feat)
                 
        if active_feats:
            print(f"  Features: {', '.join(active_feats[:6])}{'...' if len(active_feats) > 6 else ''}")

def main():
    print("Initializing Lufthansa API Client...")
    try:
        api = LufthansaAPIClient()
        api.authenticate()
        print("Authentication successful!")
    except Exception as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)

    while True:
        print("\n=== Lufthansa API: Offers ===")
        print("1. Seat Maps")
        print("2. Lounges")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == '1':
            fn = input("Flight Number (e.g. LH400) [*REQUIRED]: ").strip().upper()
            orig = input("Origin Airport (e.g. FRA) [*REQUIRED]: ").strip().upper()
            dest = input("Destination Airport (e.g. JFK) [*REQUIRED]: ").strip().upper()
            dt = input("Departure Date (e.g. 2019-07-15) [*REQUIRED]: ").strip()
            dt = format_date(dt)
            cls = input("Cabin Class (F/C/E/M) [*REQUIRED]: ").strip().upper()
            
            if not (fn and orig and dest and dt and cls):
                print("Error: All fields are required for Seat Maps.")
                continue
                
            try:
                print(f"\nFetching seat map for {fn} {orig}->{dest} on {dt} for class {cls}...")
                res = api.get_seat_maps(fn, orig, dest, dt, cls)
                if 'SeatAvailabilityResource' in res:
                     print_seat_map(res['SeatAvailabilityResource'])
                else:
                     print_seat_map(res)
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '2':
            code = input("Airport or City Code (e.g. FRA) [*REQUIRED]: ").strip().upper()
            if not code:
                print("Code is required.")
                continue
                
            print("\nYou can filter by Cabin Class OR Tier Code (not both). Press enter to skip.")
            cls = input("Cabin Class (F/C/E/M) [Optional]: ").strip().upper()
            tier = ""
            if not cls:
                tier = input("Tier Code (HON/SEN/FTL/SGC) [Optional]: ").strip().upper()
                
            lang = input("Language Code (e.g. en, de) [Default: en]: ").strip().lower()
            if not lang: lang = "en"
            
            try:
                msg = f"Fetching lounges for {code}..."
                if cls: msg += f" (Class: {cls})"
                elif tier: msg += f" (Tier: {tier})"
                print(f"\n{msg}")
                
                res = api.get_lounges(code, cabin_class=cls if cls else None, tier_code=tier if tier else None, lang=lang)
                if 'LoungeResource' in res and 'Lounges' in res['LoungeResource']:
                     print_lounges(res['LoungeResource']['Lounges'])
                else:
                     print_lounges(res)
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '3' or choice.lower() in ['exit', 'quit']:
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
