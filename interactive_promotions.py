import sys
import json
from datetime import datetime
from luftansa-api.lufthansa_api import LufthansaAPIClient

def format_date(date_str):
    """
    Tries to parse various date formats and return the strict YYYY-MM-DD format needed by the API.
    """
    if not date_str:
        return ""
        
    date_str = date_str.strip()
    formats = [
        "%Y-%m-%d", # 2026-03-04
        "%d%b%Y",   # 04MAR2026
        "%d/%m/%Y", # 04/03/2026
        "%d-%m-%Y", # 04-03-2026
        "%d%b%y",   # 04MAR26
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.upper(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
            
    # Try cleaning characters
    clean_date = date_str
    for char in ['(', ')', '!', '@', '#', '$', '%']:
        clean_date = clean_date.replace(char, '')
        
    try:
         dt = datetime.strptime(clean_date.upper(), "%d%b%Y")
         return dt.strftime("%Y-%m-%d")
    except ValueError:
         pass

    return date_str

def print_results(items):
    if not items:
        print("No price offers found.")
        return
        
    if isinstance(items, dict):
        items = [items]
        
    print(f"\n--- Price Offers ({len(items)} results) ---")
    for item in items:
        orig = item.get('origin', 'N/A')
        dest = item.get('destination', 'N/A')
        dept = item.get('departureDate', 'N/A')
        ret = item.get('returnDate', 'N/A')
        seats = item.get('seatAvailability', 'N/A')
        offer_type = item.get('offerType', 'N/A')
        
        price_info = item.get('price', {})
        amount = price_info.get('amount', 'N/A')
        currency = price_info.get('currency', 'N/A')
        
        print(f"\n[{orig} -> {dest}] {offer_type}")
        print(f"  Departure: {dept} | Return: {ret}")
        print(f"  Price: {amount} {currency} | Seats Available: {seats}")

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
        print("\n=== Lufthansa API: Partner API - Price Offers ===")
        print("Enter search parameters (press Enter to skip optional fields).")
        print("Type 'exit' or 'quit' in any field to stop.\n")
        
        origin = input("Origin City/Airport (e.g. FRA) [*REQUIRED]: ").strip().upper()
        if origin.lower() in ['exit', 'quit']: break
        if not origin: continue
        
        destination = input("Destination City/Airport (e.g. ROM) [*REQUIRED]: ").strip().upper()
        if destination.lower() in ['exit', 'quit']: break
        if not destination: continue
        
        departure_date = input("Departure Date (e.g. 2026-10-01) [*REQUIRED]: ").strip()
        if departure_date.lower() in ['exit', 'quit']: break
        if not departure_date: continue
        departure_date = format_date(departure_date)
        
        return_date = input("Return Date (e.g. 2026-10-08) [Optional]: ").strip()
        if return_date.lower() in ['exit', 'quit']: break
        return_date = format_date(return_date) if return_date else None
        
        cabin = input("Cabin Class (m/f/c/p) [Optional]: ").strip().lower()
        if cabin.lower() in ['exit', 'quit']: break
        cabin = cabin if cabin else None
        
        service = input("Service Type (amadeusBestPrice etc.) [Optional]: ").strip()
        if service.lower() in ['exit', 'quit']: break
        service = service if service else None
        
        try:
            print(f"\nFetching price offers for {origin} -> {destination}...")
            res = api.get_price_offers_flights_ond(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                service=service
            )
            
            # According to docs response could be an array of objects
            # Let's handle it gracefully
            if isinstance(res, list):
                print_results(res)
            elif isinstance(res, dict) and "flight" in res.keys():
                 print_results(res["flight"])
            else:
                print_results(res)
            
        except Exception as e:
            print(f"\nAPI Error: {e}")

if __name__ == "__main__":
    main()
