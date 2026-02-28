import os
import requests
from dotenv import load_dotenv

# Load secrets from .env file explicitly in the script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=env_path)

class LufthansaAPIClient:
    """
    A comprehensive client for the Lufthansa Open API.
    Based on documentation at: https://developer.lufthansa.com/docs/read/Home
    """
    BASE_URL = "https://api.lufthansa.com/v1"
    AUTH_URL = "https://api.lufthansa.com/v1/oauth/token"
    PARTNER_AUTH_URL = "https://api.lufthansa.com/v1/partners/oauth/token"
    
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.getenv("LUFTHANSA_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("LUFTHANSA_CLIENT_SECRET")
        self.access_token = None
        self.partner_access_token = None
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Client ID and Client Secret must be provided either as arguments or in .env file as LUFTHANSA_CLIENT_ID and LUFTHANSA_CLIENT_SECRET.")
            
    def authenticate(self):
        """Obtain an access token using client credentials."""
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(self.AUTH_URL, data=data, headers=headers)
        response.raise_for_status()
        self.access_token = response.json().get("access_token")
        return self.access_token

    def authenticate_partner(self):
        """Obtain a partner access token using client credentials."""
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(self.PARTNER_AUTH_URL, data=data, headers=headers)
        response.raise_for_status()
        self.partner_access_token = response.json().get("access_token")
        return self.partner_access_token
        
    def _request(self, endpoint, method="GET", params=None, is_partner=False):
        """Helper to make API requests with authentication."""
        # Determine which token to use based on is_partner flag
        token = self.partner_access_token if is_partner else self.access_token
        
        if not token:
            token = self.authenticate_partner() if is_partner else self.authenticate()
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        url = f"{self.BASE_URL}{endpoint}"
        
        response = requests.request(method, url, headers=headers, params=params)
        
        # Simple token refresh logic if expired
        if response.status_code == 401:
            token = self.authenticate_partner() if is_partner else self.authenticate()
            headers["Authorization"] = f"Bearer {token}"
            response = requests.request(method, url, headers=headers, params=params)
            
        response.raise_for_status()
        return response.json()

    # ==========================================
    # Offers
    # ==========================================

    def get_seat_maps(self, flight_number, origin, destination, departure_date, cabin_class):
        """Retrieve the seat map for a specific flight and cabin class."""
        path = f"/offers/seatmaps/{flight_number}/{origin}/{destination}/{departure_date}/{cabin_class}"
        return self._request(path)

    def get_lounges(self, code, cabin_class=None, tier_code=None, lang="en"):
        """Retrieve lounge information for an airport or city.
           Cannot specify both cabin_class and tier_code."""
        params = {}
        if lang: params["lang"] = lang
        if cabin_class: params["cabinClass"] = cabin_class
        elif tier_code: params["tierCode"] = tier_code
        
        return self._request(f"/offers/lounges/{code}", params=params if params else None)

    # ==========================================
    # Operations
    # ==========================================
    
    def get_public_flight_schedules(self, airlines=None, flight_number_ranges=None, start_date=None, end_date=None, days_of_operation=None, time_mode="UTC", limit=None, offset=None):
        """Retrieve public flight schedules (e.g., search by date range, airlines, flight numbers)."""
        params = {}
        if airlines: params["airlines"] = airlines
        if flight_number_ranges: params["flightNumberRanges"] = flight_number_ranges
        if start_date: params["startDate"] = start_date
        if end_date: params["endDate"] = end_date
        if days_of_operation: params["daysOfOperation"] = days_of_operation
        if time_mode: params["timeMode"] = time_mode
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        return self._request("/flight-schedules/flightschedules/passenger", params=params if params else None)

    def get_flight_schedules(self, origin, destination, from_date_time, direct_flights=False):
        """Retrieve flight schedules between two airports on a given date."""
        params = {"directFlights": 1 if direct_flights else 0}
        return self._request(f"/operations/schedules/{origin}/{destination}/{from_date_time}", params=params)

    def get_flight_status(self, flight_number, date):
        """Flight status by flight number and date."""
        return self._request(f"/operations/flightstatus/{flight_number}/{date}")

    def get_flight_status_by_route(self, origin, destination, date, service_type=None):
        """Flight status by route (origin / destination) and date."""
        params = {"serviceType": service_type} if service_type else None
        return self._request(f"/operations/flightstatus/route/{origin}/{destination}/{date}", params=params)

    def get_flight_status_at_arrival(self, airport_code, from_date_time, service_type=None, limit=None, offset=None):
        """Flight status for flights arriving at a given airport."""
        params = {}
        if service_type: params["serviceType"] = service_type
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        return self._request(f"/operations/flightstatus/arrivals/{airport_code}/{from_date_time}", params=params if params else None)

    def get_flight_status_at_departure(self, airport_code, from_date_time, service_type=None, limit=None, offset=None):
        """Flight status for flights departing from a given airport."""
        params = {}
        if service_type: params["serviceType"] = service_type
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        return self._request(f"/operations/flightstatus/departures/{airport_code}/{from_date_time}", params=params if params else None)

    def get_customer_flight_information(self, flight_number, date, limit=None, offset=None):
        """Customer Flight Information by Flight Number and Date."""
        params = {}
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        return self._request(f"/operations/customerflightinformation/{flight_number}/{date}", params=params if params else None)

    def get_customer_flight_information_by_route(self, origin, destination, date, limit=None, offset=None):
        params = {}
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        return self._request(f"/operations/customerflightinformation/route/{origin}/{destination}/{date}", params=params if params else None)

    def get_customer_flight_information_at_arrival(self, airport_code, from_date_time, limit=None, offset=None):
        params = {}
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        return self._request(f"/operations/customerflightinformation/arrivals/{airport_code}/{from_date_time}", params=params if params else None)

    def get_customer_flight_information_at_departure(self, airport_code, from_date_time, limit=None, offset=None):
        params = {}
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        return self._request(f"/operations/customerflightinformation/departures/{airport_code}/{from_date_time}", params=params if params else None)

    # ==========================================
    # Reference Data
    # ==========================================
    
    def get_countries(self, country_code=None, lang=None, limit=None, offset=None):
        endpoint = f"/mds-references/countries/{country_code}" if country_code else "/mds-references/countries"
        params = {}
        if lang: params["lang"] = lang
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        return self._request(endpoint, params=params if params else None)

    def get_cities(self, city_code=None, lang=None, limit=None, offset=None):
        endpoint = f"/mds-references/cities/{city_code}" if city_code else "/mds-references/cities"
        params = {}
        if lang: params["lang"] = lang
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        return self._request(endpoint, params=params if params else None)

    def get_airports(self, airport_code=None, lang=None, limit=None, offset=None, lh_operated=False):
        endpoint = f"/mds-references/airports/{airport_code}" if airport_code else "/mds-references/airports"
        params = {}
        if lang: params["lang"] = lang
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        if lh_operated: params["LHoperated"] = 1
        return self._request(endpoint, params=params if params else None)

    def get_nearest_airports(self, latitude, longitude, lang=None):
        params = {"lang": lang} if lang else None
        return self._request(f"/references/airports/nearest/{latitude},{longitude}", params=params)

    def get_airlines(self, airline_code=None, limit=None, offset=None):
        endpoint = f"/mds-references/airlines/{airline_code}" if airline_code else "/mds-references/airlines"
        params = {}
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        return self._request(endpoint, params=params if params else None)

    def get_aircraft(self, aircraft_code=None, limit=None, offset=None):
        endpoint = f"/mds-references/aircraft/{aircraft_code}" if aircraft_code else "/mds-references/aircraft"
        params = {}
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        return self._request(endpoint, params=params if params else None)

    def get_seat_details(self, aircraft_code, cabin_code, lang=None):
        params = {"lang": lang} if lang else None
        return self._request(f"/references/seatdetails/{aircraft_code}/{cabin_code}", params=params)

    # ==========================================
    # Offers
    # ==========================================
    
    def get_seat_maps(self, flight_number, origin, destination, date, cabin_class):
        return self._request(f"/offers/seatmaps/{flight_number}/{origin}/{destination}/{date}/{cabin_class}")

    def get_lounges(self, airport_code, cabin_class=None, tier_code=None, lang=None):
        params = {}
        if cabin_class: params["cabinClass"] = cabin_class
        if tier_code: params["tierCode"] = tier_code
        if lang: params["lang"] = lang
        return self._request(f"/offers/lounges/{airport_code}", params=params if params else None)

    def get_lowest_fares(self, origin, destination, travel_date):
        return self._request(f"/offers/fares/lowestfare", params={
            "origin": origin, "destination": destination, "travelDate": travel_date
        })

    def get_best_fares(self):
        # Parameters would be highly specific, refer to docs
        return self._request(f"/offers/fares/bestfares")
        
    def get_fares_subscriptions(self, origin, destination):
        # Parameters would be highly specific, refer to docs
        return self._request(f"/offers/fares/subscriptions", params={
             "origin": origin, "destination": destination
        })
        
    # ==========================================
    # Promotions
    # ==========================================
    
    def get_price_offers_flights_ond(self, origin, destination, departure_date, return_date=None, service=None):
        params = {"departureDate": departure_date}
        if return_date: params["returnDate"] = return_date
        if service: params["service"] = service
        return self._request(f"/promotions/priceoffers/flights/ond/{origin}/{destination}", params=params, is_partner=True)

    def get_price_offers_ond(self, origin, destination, departure_date, return_date=None, cabin=None, request_country=None, service=None):
        params = {"departureDate": departure_date}
        if return_date: params["returnDate"] = return_date
        if cabin: params["cabin"] = cabin
        if request_country: params["requestCountry"] = request_country
        if service: params["service"] = service
        return self._request(f"/promotions/priceoffers/ond/{origin}/{destination}", params=params, is_partner=True)

    # ==========================================
    # Flight Ops / Crew Services
    # ==========================================

    def get_crew_airport_weather(self, station=None):
        params = {"station": station} if station else None
        return self._request("/flight_operations/crew_services/COMMON_AIRPORT_WEATHER", params=params)

    def get_crew_check_in_times(self):
        return self._request("/flight_operations/crew_services/COMMON_CHECK_IN_TIMES")

    def get_crew_list(self, flight_designator, flight_date, departure_airport, arrival_airport, access_code):
        params = {
            "flightDesignator": flight_designator,
            "flightDate": flight_date,
            "departureAirport": departure_airport,
            "arrivalAirport": arrival_airport,
            "accessCode": access_code
        }
        return self._request("/flight_operations/crew_services/COMMON_CREWLIST", params=params)

    def get_crew_hotel_info(self, station=None, provider=None):
        params = {}
        if station: params["station"] = station
        if provider: params["provider"] = provider
        return self._request("/flight_operations/crew_services/COMMON_CREW_HOTEL_INFO", params=params if params else None)

    def get_crew_rotation(self, rn=None):
        params = {"RN": rn} if rn else None
        return self._request("/flight_operations/crew_services/COMMON_CREW_ROTATION", params=params)

    def get_crew_duty_events(self, from_date=None, to_date=None):
        params = {}
        if from_date: params["fromDate"] = from_date
        if to_date: params["toDate"] = to_date
        return self._request("/flight_operations/crew_services/COMMON_DUTY_EVENTS", params=params if params else None)

    def get_flight_leg_details(self):
        return self._request("/flight_operations/crew_services/COMMON_FLIGHT_LEG_DETAILS")

    def get_landing_report(self, flight_designator=None, flight_date=None, departure_airport=None):
        params = {}
        if flight_designator: params["flightDesignator"] = flight_designator
        if flight_date: params["flightDate"] = flight_date
        if departure_airport: params["departureAirport"] = departure_airport
        return self._request("/flight_operations/crew_services/COMMON_LANDING_REPORT", params=params if params else None)

    def get_simulator_crewlist(self, for_date, access_code=None):
        params = {"forDate": for_date}
        if access_code: params["accessCode"] = access_code
        return self._request("/flight_operations/crew_services/COMMON_SIMULATOR_CREWLIST", params=params)

    # ==========================================
    # Cargo
    # ==========================================

    def get_cargo_shipment_tracking(self, awb_prefix, awb_number):
        return self._request(f"/cargo/shipmentTracking/{awb_prefix}-{awb_number}")

    # ==========================================
    # Customer Deeplinks
    # ==========================================
    
    def get_booking_servicing_deeplinks(self, pnr, last_name):
        return self._request(f"/customer-deeplinks/booking", params={"pnr": pnr, "lastName": last_name})
        
    def get_checkin_deeplinks(self, pnr, last_name, origin=None):
        params = {"pnr": pnr, "lastName": last_name}
        if origin:
            params["origin"] = origin
        return self._request(f"/customer-deeplinks/checkin", params=params)

    def get_shopping_links_search(self, origin, destination, date):
        return self._request(f"/customer-deeplinks/shopping", params={"origin": origin, "destination": destination, "date": date})
        

if __name__ == "__main__":
    # Example usage
    # Make sure you have your client ID and secret in the .env file
    try:
        api = LufthansaAPIClient()
        print("Authenticating...")
        api.authenticate()
        print(f"Token acquired. Ready to make requests.")
        
        # Fetch available countries
        print("Fetching countries...")
        countries = api.get_countries()
        print(f"Retrieved response containing {len(countries) if isinstance(countries, list) else 'data'}.")
        
        # Test Reference Data endpoint
        fra_airport = api.get_airports('FRA')
        print("Information for FRA Airport:", fra_airport)

    except Exception as e:
        print(f"Error initializing client or making requests: {e}")
