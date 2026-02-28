import os
from flask import Flask, render_template, request, jsonify
from luftansa-api.lufthansa_api import LufthansaAPIClient

app = Flask(__name__)

# Initialize the API client globally (it handles its own token refresh)
try:
    lufthansa_api = LufthansaAPIClient()
    lufthansa_api.authenticate()
    print("Successfully authenticated with Lufthansa API.")
except Exception as e:
    print(f"Failed to authenticate on startup: {e}")
    # We don't exit in case the .env is missing but added later
    lufthansa_api = None


@app.route("/")
def index():
    """Serve the main single-page application."""
    return render_template("index.html")


@app.route("/api/schedules", methods=["GET"])
def get_schedules():
    """API Endpoint for Flight Schedules."""
    if not lufthansa_api:
        return jsonify({"error": "API Client not initialized."}), 500
        
    origin = request.args.get("origin")
    dest = request.args.get("dest")
    date = request.args.get("date")
    direct = request.args.get("direct", "false").lower() == "true"
    
    if not all([origin, dest, date]):
        return jsonify({"error": "Missing required parameters: origin, dest, date"}), 400
        
    try:
        result = lufthansa_api.get_flight_schedules(origin, dest, date, direct_flights=direct)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/customer-info/flight", methods=["GET"])
def get_flight_info():
    """API Endpoint for Customer Info by Flight Number."""
    if not lufthansa_api:
        return jsonify({"error": "API Client not initialized."}), 500
        
    flight_num = request.args.get("flight_num")
    date = request.args.get("date")
    
    if not all([flight_num, date]):
        return jsonify({"error": "Missing required parameters: flight_num, date"}), 400
        
    try:
        result = lufthansa_api.get_customer_flight_information(flight_num, date)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/customer-info/route", methods=["GET"])
def get_route_info():
    """API Endpoint for Customer Info by Route."""
    if not lufthansa_api:
        return jsonify({"error": "API Client not initialized."}), 500
        
    origin = request.args.get("origin")
    dest = request.args.get("dest")
    date = request.args.get("date")
    
    if not all([origin, dest, date]):
        return jsonify({"error": "Missing required parameters: origin, dest, date"}), 400
        
    try:
        result = lufthansa_api.get_customer_flight_information_by_route(origin, dest, date)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/customer-info/arrivals", methods=["GET"])
def get_arrival_info():
    """API Endpoint for Customer Info at Arrival Airport."""
    if not lufthansa_api:
        return jsonify({"error": "API Client not initialized."}), 500
        
    airport = request.args.get("airport")
    from_time = request.args.get("from_time")
    
    if not all([airport, from_time]):
        return jsonify({"error": "Missing required parameters: airport, from_time"}), 400
        
    try:
        result = lufthansa_api.get_flight_status_at_arrival(airport, from_time)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        

@app.route("/api/customer-info/departures", methods=["GET"])
def get_departure_info():
    """API Endpoint for Customer Info at Departure Airport."""
    if not lufthansa_api:
        return jsonify({"error": "API Client not initialized."}), 500
        
    airport = request.args.get("airport")
    from_time = request.args.get("from_time")
    
    if not all([airport, from_time]):
        return jsonify({"error": "Missing required parameters: airport, from_time"}), 400
        
    try:
        result = lufthansa_api.get_flight_status_at_departure(airport, from_time)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
