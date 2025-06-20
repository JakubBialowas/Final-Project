import requests
import json
from datetime import datetime # Import datetime for date/time conversion

# Base URL for the GIOŚ API. This is the corrected base URL for the 'pjp-api/rest' services.
GIOS_API_BASE_URL = "https://api.gios.gov.pl/pjp-api/rest"

def fetch_stations():
    """
    Fetches a list of all available air quality measurement stations from the GIOŚ API.

    The API endpoint used is: https://api.gios.gov.pl/pjp-api/rest/station/findAll

    Returns:
        list: A list of dictionaries, where each dictionary represents a station
              and contains its details (e.g., id, stationName, address, geographical coordinates).
              Returns None if there's an error during the API call.
    """
    url = f"{GIOS_API_BASE_URL}/station/findAll"
    try:
        # Send an HTTP GET request to the /station/findAll endpoint
        response = requests.get(url, timeout=10) # Added a timeout for robustness
        
        # Raise an HTTPError for bad responses (4xx or 5xx status codes)
        response.raise_for_status() 
        
        # Parse the JSON response body and return it
        return response.json()
    except requests.exceptions.RequestException as e:
        # Catch any request-related errors (e.g., network issues, timeouts, HTTP errors)
        print(f"Błąd pobierania stacji z GIOŚ API: {e}")
        return None

def fetch_sensors_for_station(station_id):
    """
    Fetches a list of sensors (measurement positions) for a given air quality station ID
    from the GIOŚ API.

    The API endpoint used is: https://api.gios.gov.pl/pjp-api/rest/station/sensors/{station_id}

    Args:
        station_id (int): The unique identifier of the air quality station.

    Returns:
        list: A list of dictionaries, where each dictionary represents a sensor
              and contains its details (e.g., id, stationId, param details).
              Returns None if there's an error during the API call.
    """
    url = f"{GIOS_API_BASE_URL}/station/sensors/{station_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Błąd pobierania sensorów dla stacji {station_id} z GIOŚ API: {e}")
        return None

def fetch_measurements_for_sensor(sensor_id):
    """
    Fetches specific measurement data for a given sensor ID from the GIOŚ API.

    The API endpoint used is: https://api.gios.gov.pl/pjp-api/rest/data/getData/{sensor_id}

    Args:
        sensor_id (int): The unique identifier of the measurement sensor.

    Returns:
        dict: A dictionary containing the measurement data, typically with a 'key' (parameter code)
              and 'values' (a list of dictionaries, each with 'date' and 'value').
              Returns None if there's an error during the API call.
    """
    url = f"{GIOS_API_BASE_URL}/data/getData/{sensor_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Błąd pobierania pomiarów dla sensora {sensor_id} z GIOŚ API: {e}")
        return None

def process_measurement_data(raw_measurements_data):
    """
    Processes raw measurement data fetched from the GIOŚ API.
    Converts 'date' strings to datetime objects and 'value' strings to floats.
    Handles 'null' values for 'value' by converting them to None.

    Args:
        raw_measurements_data (dict): The dictionary returned by fetch_measurements_for_sensor.
                                      Expected format: {'key': 'PARAM_CODE', 'values': [{'date': '...', 'value': '...'}, ...]}

    Returns:
        dict: A processed dictionary with 'values' containing dictionaries where 'date' is a datetime object
              and 'value' is a float or None. Returns None if the input is invalid or essential keys are missing.
    """
    if not raw_measurements_data or 'values' not in raw_measurements_data:
        print("Błąd: Nieprawidłowe dane pomiarowe do przetworzenia.")
        return None

    processed_data = {'key': raw_measurements_data.get('key')}
    processed_values = []

    for item in raw_measurements_data.get('values', []):
        date_str = item.get('date')
        value_str = item.get('value')

        # Convert date string to datetime object
        parsed_date = None
        if date_str:
            try:
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                print(f"Ostrzeżenie: Nieprawidłowy format daty: {date_str}")
                parsed_date = None # Keep it None if parsing fails

        # Convert value string to float, handling 'null'
        parsed_value = None
        if value_str is not None: # Check for actual None from JSON (Python's None)
            try:
                parsed_value = float(value_str)
            except (ValueError, TypeError):
                print(f"Ostrzeżenie: Nieprawidłowa wartość liczbowa: {value_str}")
                parsed_value = None # Keep it None if conversion fails
        
        # If value_str was "null" from JSON, it will already be None in Python due to json.loads()

        processed_values.append({
            'date': parsed_date,
            'value': parsed_value
        })
    
    processed_data['values'] = processed_values
    return processed_data


# Example usage (for testing this module independently if desired):
if __name__ == "__main__":
    print("--- Fetching all stations ---")
    stations = fetch_stations()
    if stations:
        print(f"Pobrano {len(stations)} stacji.")
        # Optional: Print details of the first 3 stations for brevity
        # for i, station in enumerate(stations[:3]):
        #     print(json.dumps(station, indent=2, ensure_ascii=False))
        # print("--- End of first 3 stations ---")

        # Example: Try to find a station with available sensors to test measurement fetching
        found_station_id = None
        for s in stations:
            # Look for a station that might have sensors. This is a heuristic.
            # In a real app, you'd integrate this with your GUI's selection.
            if s.get('id'): # Just pick the first one with an ID for this example
                found_station_id = s['id']
                print(f"\nUżywam stacji ID {found_station_id} do testowania sensorów.")
                break
        
        if found_station_id:
            print(f"\n--- Fetching sensors for station ID {found_station_id} ---")
            sensors = fetch_sensors_for_station(found_station_id)
            if sensors:
                print(f"Pobrano {len(sensors)} sensorów dla stacji {found_station_id}.")
                
                # Check if there's at least one sensor and try to fetch its measurements
                if sensors:
                    first_sensor = sensors[0]
                    sample_sensor_id = first_sensor['id']
                    print(f"Pierwszy sensor dla stacji {found_station_id}: ID={sample_sensor_id}, Parametr={first_sensor['param']['paramName']}")
                    
                    print(f"\n--- Fetching measurements for sensor ID {sample_sensor_id} ---")
                    raw_measurements = fetch_measurements_for_sensor(sample_sensor_id)
                    if raw_measurements:
                        print(f"Pobrano surowe dane pomiarowe dla sensora {sample_sensor_id}.")
                        # print("Surowe dane (pierwsze 2 wpisy):")
                        # print(json.dumps(raw_measurements.get('values', [])[:2], indent=2, ensure_ascii=False))

                        # Process the fetched raw data
                        processed_measurements = process_measurement_data(raw_measurements)
                        if processed_measurements:
                            print(f"\nPobrano i przetworzono dane pomiarowe dla sensora {sample_sensor_id}. Klucz: {processed_measurements.get('key')}")
                            print("Przetworzone dane (pierwsze 5 wpisów):")
                            for entry in processed_measurements.get('values', [])[:5]:
                                print(f"  Data: {entry['date']}, Wartość: {entry['value']}")
                            print("--- Koniec pierwszych 5 pomiarów ---")
                        else:
                            print(f"Nie udało się przetworzyć danych pomiarowych dla sensora {sample_sensor_id}.")
                    else:
                        print(f"Nie udało się pobrać surowych pomiarów dla sensora {sample_sensor_id}.")
                else:
                    print(f"Brak sensorów dla stacji ID {found_station_id}.")
            else:
                print(f"Nie udało się pobrać sensorów dla stacji {found_station_id}.")
        else:
            print("Nie znaleziono żadnej stacji do testowania sensorów.")
    else:
        print("Nie udało się pobrać żadnych stacji.")