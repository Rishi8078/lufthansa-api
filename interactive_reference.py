import sys
import json
from luftansa-api.lufthansa_api import LufthansaAPIClient

def get_name(item):
    """Helper to extract English name from Names object"""
    names = item.get("Names", {}).get("Name", [])
    if isinstance(names, dict):
        names = [names]
    for n in names:
        if n.get("@LanguageCode") == "EN":
            return n.get("$")
    # Fallback to the first available name
    if names and isinstance(names, list) and len(names) > 0:
        return names[0].get("$", "Unknown")
    return "Unknown"

def print_results(items, title="Records"):
    if not items:
        print("No records found.")
        return
        
    if isinstance(items, dict):
        items = [items]
        
    print(f"\n--- {title} (Showing up to 20 results) ---")
    for item in items[:20]:
        # Aircraft
        if "AircraftCode" in item:
            print(f"[{item.get('AircraftCode')}] {get_name(item)}")
        # Airlines
        elif "AirlineID" in item:
            print(f"[{item.get('AirlineID')} / {item.get('AirlineID_ICAO', 'N/A')}] {get_name(item)}")
        # Airports
        elif "AirportCode" in item:
            city_code = item.get("CityCode", "")
            country_code = item.get("CountryCode", "")
            time_zone = item.get("TimeZone", {}).get("TotalOffset", "")
            print(f"[{item.get('AirportCode')}] {get_name(item)} (City: {city_code}, Country: {country_code}, GMT{time_zone})")
            if "Distance" in item:
                print(f"  Distance: {item.get('Distance', {}).get('Value')} {item.get('Distance', {}).get('UOM')}")
        # Cities
        elif "CityCode" in item:
            print(f"[{item.get('CityCode')}] {get_name(item)} (Country: {item.get('CountryCode', '')})")
        # Countries
        elif "CountryCode" in item:
            print(f"[{item.get('CountryCode')}] {get_name(item)}")
        else:
            # Fallback
            print(json.dumps(item, indent=2))
            
    if len(items) > 20:
        print(f"... and {len(items)-20} more records.")

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
        print("\n=== Lufthansa API: Reference Data Menu ===")
        print("1. Get Countries")
        print("2. Get Cities")
        print("3. Get Airports")
        print("4. Get Nearest Airport")
        print("5. Get Airlines")
        print("6. Get Aircraft")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()

        try:
            if choice == "1":
                code = input("Country Code (e.g. DE) or leave blank for all: ").strip().upper()
                lang = input("Language (e.g. EN) or leave blank: ").strip().upper()
                print("Fetching countries...")
                res = api.get_countries(country_code=code if code else None, lang=lang if lang else None)
                items = res.get("CountryResource", {}).get("Countries", {}).get("Country", [])
                print_results(items, "Countries")

            elif choice == "2":
                code = input("City Code (e.g. FRA) or leave blank for all: ").strip().upper()
                lang = input("Language (e.g. EN) or leave blank: ").strip().upper()
                print("Fetching cities...")
                res = api.get_cities(city_code=code if code else None, lang=lang if lang else None)
                items = res.get("CityResource", {}).get("Cities", {}).get("City", [])
                print_results(items, "Cities")

            elif choice == "3":
                code = input("Airport Code (e.g. FRA) or leave blank for all: ").strip().upper()
                lang = input("Language (e.g. EN) or leave blank: ").strip().upper()
                print("Fetching airports...")
                res = api.get_airports(airport_code=code if code else None, lang=lang if lang else None)
                items = res.get("AirportResource", {}).get("Airports", {}).get("Airport", [])
                print_results(items, "Airports")

            elif choice == "4":
                lat = input("Latitude (e.g. 50.0): ").strip()
                lon = input("Longitude (e.g. 8.5): ").strip()
                lang = input("Language (e.g. EN) or leave blank: ").strip().upper()
                if not lat or not lon:
                    print("Latitude and Longitude are required.")
                    continue
                print("Fetching nearest airports...")
                res = api.get_nearest_airports(latitude=lat, longitude=lon, lang=lang if lang else None)
                items = res.get("NearestAirportResource", {}).get("Airports", {}).get("Airport", [])
                print_results(items, "Nearest Airports")

            elif choice == "5":
                code = input("Airline Code (e.g. LH) or leave blank for all: ").strip().upper()
                print("Fetching airlines...")
                res = api.get_airlines(airline_code=code if code else None)
                items = res.get("AirlineResource", {}).get("Airlines", {}).get("Airline", [])
                print_results(items, "Airlines")

            elif choice == "6":
                code = input("Aircraft Code (e.g. 320) or leave blank for all: ").strip().upper()
                print("Fetching aircraft...")
                res = api.get_aircraft(aircraft_code=code if code else None)
                items = res.get("AircraftResource", {}).get("AircraftSummaries", {}).get("AircraftSummary", [])
                print_results(items, "Aircraft")

            elif choice == "7":
                print("Exiting...")
                break
                
            else:
                print("Invalid choice. Please enter a number from 1 to 7.")
                
        except Exception as e:
            print(f"\nAPI Error: {e}")

if __name__ == "__main__":
    main()
