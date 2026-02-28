import sys
from luftansa-api.lufthansa_api import LufthansaAPIClient

def print_flight(schedule):
    """Helper to pretty-print a flight schedule object."""
    duration = schedule.get("TotalJourney", {}).get("Duration", "Unknown")
    
    # The API might return a single Dictionary or a list for flights depending on connections
    flight_data = schedule.get("Flight", {})
    if isinstance(flight_data, dict):
        flights = [flight_data]
    else:
        flights = flight_data
        
    for index, flight in enumerate(flights):
        departure = flight.get("Departure", {})
        arrival = flight.get("Arrival", {})
        carrier = flight.get("MarketingCarrier", {})
        
        flight_num = f"{carrier.get('AirlineID')}{carrier.get('FlightNumber')}"
        dep_time = departure.get("ScheduledTimeLocal", {}).get("DateTime", "Unknown")
        arr_time = arrival.get("ScheduledTimeLocal", {}).get("DateTime", "Unknown")
        
        dep_term = departure.get("Terminal", {}).get("Name", "")
        arr_term = arrival.get("Terminal", {}).get("Name", "")
        equipment = flight.get("Equipment", {}).get("AircraftCode", "Unknown")
        
        dep_str = f"{departure.get('AirportCode')} T{dep_term}" if dep_term else departure.get('AirportCode')
        arr_str = f"{arrival.get('AirportCode')} T{arr_term}" if arr_term else arrival.get('AirportCode')
        
        prefix = f"Leg {index+1}:" if len(flights) > 1 else "Flight:"
        print(f"  {prefix} {flight_num} (Aircraft: {equipment})")
        print(f"    Departing: {dep_str} at {dep_time}")
        print(f"    Arriving : {arr_str} at {arr_time}")
    
    print(f"  Total Duration: {duration}")
    print("-" * 50)

def main():
    print("Initializing Lufthansa API Client...")
    try:
        api = LufthansaAPIClient()
        api.authenticate()
        print("Authentication successful!")
    except Exception as e:
        print(f"Authentication failed: {e}")
        print("Please check your .env file credentials and ensure your app is subscribed to the Public API plan.")
        sys.exit(1)

    while True:
        print("\n=== Lufthansa API: Operations Menu ===")
        print("1. Get Flight Schedules (origin -> destination)")
        print("2. Get Customer Flight Info (by flight number and date)")
        print("3. Get Customer Flight Info by Route (origin -> destination)")
        print("4. Get Customer Flight Info at Arrival Airport")
        print("5. Get Customer Flight Info at Departure Airport")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()

        try:
            if choice == "1":
                print("\n--- Flight Schedules ---")
                origin = input("Origin Airport Code (e.g. FRA): ").strip().upper()
                dest = input("Destination Airport Code (e.g. JFK): ").strip().upper()
                date = input("Date (YYYY-MM-DD): ").strip()
                direct_ans = input("Direct flights only? (y/N): ").strip().lower()
                direct = direct_ans == "y"
                
                print(f"\nFetching schedules for {origin} -> {dest} on {date}...")
                result = api.get_flight_schedules(origin, dest, date, direct_flights=direct)
                
                schedules = result.get("ScheduleResource", {}).get("Schedule", [])
                if not schedules:
                    print("No schedules found.")
                else:
                    if isinstance(schedules, dict):
                        schedules = [schedules]
                    print(f"\nFound {len(schedules)} schedule(s):")
                    for s in schedules:
                        print_flight(s)

            elif choice in ("2", "3", "4", "5"):
                if choice == "2":
                    print("\n--- Customer Flight Info ---")
                    flight_num = input("Flight Number (e.g. LH400): ").strip().upper()
                    date = input("Date (YYYY-MM-DD): ").strip()
                    print(f"\nFetching info for {flight_num} on {date}...")
                    result = api.get_customer_flight_information(flight_num, date)
                elif choice == "3":
                    print("\n--- Customer Flight Info by Route ---")
                    origin = input("Origin Airport Code (e.g. FRA): ").strip().upper()
                    dest = input("Destination Airport Code (e.g. JFK): ").strip().upper()
                    date = input("Date (YYYY-MM-DD): ").strip()
                    print(f"\nFetching info for {origin} -> {dest} on {date}...")
                    result = api.get_customer_flight_information_by_route(origin, dest, date)
                elif choice == "4":
                    print("\n--- Customer Flight Info at Arrival Airport ---")
                    airport = input("Arrival Airport Code (e.g. JFK): ").strip().upper()
                    from_time = input("From Date/Time (YYYY-MM-DDTHH:mm): ").strip()
                    print(f"\nFetching arriving flights at {airport} from {from_time}...")
                    result = api.get_customer_flight_information_at_arrival(airport, from_time)
                else:
                    print("\n--- Customer Flight Info at Departure Airport ---")
                    airport = input("Departure Airport Code (e.g. FRA): ").strip().upper()
                    from_time = input("From Date/Time (YYYY-MM-DDTHH:mm): ").strip()
                    print(f"\nFetching departing flights from {airport} from {from_time}...")
                    result = api.get_customer_flight_information_at_departure(airport, from_time)

                flights = result.get("FlightInformation", {}).get("Flights", {}).get("Flight", [])
                
                if not flights:
                    print("No flight status found.")
                else:
                    if isinstance(flights, dict):
                        flights = [flights]
                    
                    print(f"\nFound {len(flights)} flight(s):")
                    for f in flights:
                        dep = f.get("Departure", {})
                        arr = f.get("Arrival", {})
                        
                        # Marketing / Operating Carriers
                        mc_list = f.get("MarketingCarrierList", {}).get("MarketingCarrier", {})
                        if isinstance(mc_list, list) and len(mc_list) > 0:
                            mc = mc_list[0]
                        elif isinstance(mc_list, dict):
                            mc = mc_list
                        else:
                            mc = f.get("MarketingCarrier", {})
                            
                        oc = f.get("OperatingCarrier", {})
                        fnum = f"{mc.get('AirlineID', '')}{mc.get('FlightNumber', '')}"
                        op_fnum = f"{oc.get('AirlineID', '')}{oc.get('FlightNumber', '')}"
                        op_str = f" (Operated by {op_fnum})" if op_fnum and op_fnum != fnum else ""
                        
                        equipment = f.get("Equipment", {}).get("AircraftCode", "Unknown")
                        
                        # Overall Status
                        status_obj = f.get("Status", f.get("FlightStatus", {}))
                        status_code = status_obj.get("Code", "UNKNOWN")
                        status_def = status_obj.get("Description", status_obj.get("Definition", "Unknown Status"))
                        
                        print(f"Flight {fnum}{op_str} | Aircraft: {equipment} | Status: {status_code} ({status_def})")
                        
                        def print_leg_status(leg_data, leg_name):
                            airport = leg_data.get("AirportCode", "")
                            term = leg_data.get("Terminal", {}).get("Name", "")
                            gate = leg_data.get("Terminal", {}).get("Gate", "")
                            term_str = f"T{term}" if term else ""
                            gate_str = f"Gate {gate}" if gate else ""
                            loc = " ".join(filter(None, [airport, term_str, gate_str]))
                            
                            sched = leg_data.get("ScheduledTimeLocal", {}).get("DateTime", leg_data.get("Scheduled", {}).get("DateTime", "N/A"))
                            est = leg_data.get("EstimatedTimeLocal", {}).get("DateTime", leg_data.get("Estimated", {}).get("DateTime", ""))
                            act = leg_data.get("ActualTimeLocal", {}).get("DateTime", leg_data.get("Actual", {}).get("DateTime", ""))
                            
                            time_status = leg_data.get("TimeStatus", {}).get("Definition", leg_data.get("Status", {}).get("Description", ""))
                            
                            time_str = f"Scheduled: {sched}"
                            if act: time_str += f" | Actual: {act}"
                            elif est: time_str += f" | Est: {est}"
                            
                            if time_status: time_str += f" [{time_status}]"
                            
                            print(f"  {leg_name}: {loc}")
                            print(f"    {time_str}")

                        print_leg_status(dep, "Departs")
                        print_leg_status(arr, "Arrives")
                        print("-" * 50)

            elif choice == "6":
                print("Exiting...")
                break
            
            else:
                print("Invalid choice. Please enter a number from 1 to 6.")
                
        except Exception as e:
            # Usually happens if the API returns a 404 (Flight not found) or 401
            print(f"\nAPI Error: {e}")

if __name__ == "__main__":
    main()
