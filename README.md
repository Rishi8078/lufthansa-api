# Lufthansa API Integration

A comprehensive, interactive Python client and command-line toolset for exploring the **Lufthansa Open API**. 

This repository provides an easy-to-use wrapper around Lufthansa's public and partner APIs, including smart date parsing, automatic token refresh, and clean console outputs. It also includes a Flask-based web server for a graphical interface.

## 🛠️ Prerequisites & Setup

1. **Get API Credentials:** Register at the [Lufthansa Developer Portal](https://developer.lufthansa.com/) to get a Client ID and Client Secret. 
2. **Environment File:** Create a `.env` file in the root directory and add your credentials:
   ```env
   LUFTHANSA_CLIENT_ID=your_client_id_here
   LUFTHANSA_CLIENT_SECRET=your_client_secret_here
   ```
3. **Install Requirements:** Make sure you have the necessary libraries installed (e.g. `requests`, `python-dotenv`, `flask`).
   ```bash
   pip install requests python-dotenv flask
   ```

## 🚀 Usage

You can interact with the API in two ways: via the modular Command-Line Interface (CLI) scripts, or via the Flask web app frontend.

### 1. Terminal CLI Scripts

The project includes several interactive scripts corresponding to different Lufthansa API domains. Run any of them directly with Python:

```bash
python interactive_operations.py
```

These scripts provide an interactive menu, accept various flexible date formats (e.g. `04MAR26` or `2026-03-04`), and display neatly parsed data tables in your console.

### 2. Web Application

If you prefer a graphical interface, you can boot up the Flask app:

```bash
python app.py
```
This will start a local web server (usually at `http://localhost:5000`) where you can search for flight statuses via a sleek, modern UI.

---

## 📁 Repository Structure / File Explanations

### Core Library
* **`lufthansa_api.py`** 
  The central nervous system of this project. It defines the `LufthansaAPIClient` class, handling all OAuth 2.0 authentication (including automatic token refreshes) and provides clean Python methods for all supported Lufthansa API endpoints. It natively supports both the "Public" APIs and "Partner" APIs.

### Interactive CLI Scripts
These scripts import the client and provide user-friendly prompts to query the API from your terminal.

* **`interactive_operations.py`** 
  Queries the **Operations API**. Allows you to check live Flight Status and Customer Flight Information. You can search by specific Flight Number, by Route (Origin/Destination), or by Arrival/Departure Airport.
  
* **`interactive_offers.py`** 
  Queries the **Offers API**. Use this to retrieve Aircraft Seat Maps (including seat characteristics like Window/Aisle/Exit Row) and details about Lufthansa Lounges at various airports.

* **`interactive_public_schedules.py`**
  Queries the **Public Flight Schedules API**. Allows you to look up scheduled flights between dates, for specific airlines, or specific flight numbers.

* **`interactive_reference.py`**
  Queries the **Reference Data API**. A helpful utility to look up generic aviation data, including IATA Codes, full lists of Countries, Cities, Airports, Airlines, Aircraft types, and even finding the Nearest Airport using geographic coordinates.

* **`interactive_promotions.py`**
  Queries the **Partner Promotions API**. Used to fetch Price Offers (Lowest Fares) for flights. *Note: This requires a Partner-tier API credential from Lufthansa.*

### Web & Environment
* **`app.py`** 
  A Flask backend wrapper that serves a graphical web page and provides internal API routes (AJAX) to query flight statuses using the `LufthansaAPIClient`.
* **`.env`** 
  (Not tracked in git) Stores your sensitive API keys securely.
