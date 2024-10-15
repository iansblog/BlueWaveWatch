import requests
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from models import MarineWeatherData
from db import session  # Import your session from db.py

def fetch_marine_weather_from_web(latitude, longitude):
    """
    Fetch marine weather data from the Open-Meteo Marine Weather API for given latitude and longitude.

    Args:
        latitude (float): Latitude coordinate.
        longitude (float): Longitude coordinate.

    Returns:
        dict: A dictionary containing marine weather information.
    """
#    base_url = f"https://api.open-meteo.com/v1/marine"
#    params = {
#        "latitude": latitude,
#        "longitude": longitude,
#        "timezone": "auto",  # Automatically adjust timezone
#        "current_weather": "true",  # Get current marine weather data
#    }
# 
    base_url = "https://marine-api.open-meteo.com/v1/marine"
    params = {
    	"latitude": 54.544587,
    	"longitude": 10.227487,
    	"current_weather": "true"  # Get current marine weather data
    }    

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises error for bad responses
        return response.json()  # Returns the JSON response
    except requests.RequestException as e:
        print(f"Error fetching marine weather data: {e}")
        return None


def fetch_marine_weather(latitude, longitude):
    """
    Fetch marine weather data for the given latitude and longitude.
    Checks if the data exists in the cache and is less than 60 minutes old.
    If not, fetches new data and updates the cache.

    Args:
        latitude (float): Latitude coordinate.
        longitude (float): Longitude coordinate.

    Returns:
        dict: A dictionary containing structured marine weather data.
    """
    current_time = datetime.now()

    # Query the database for cached marine data for the specific location
    cached_data = session.query(MarineWeatherData).filter_by(latitude=latitude, longitude=longitude).first()

    # If cached data exists and is less than 60 minutes old, return it
    if cached_data and current_time - cached_data.last_updated < timedelta(minutes=60):
        print(f"Returning cached marine weather data for {latitude}, {longitude}.")
        return json.loads(cached_data.data)

    # Otherwise, fetch new marine weather data
    print(f"Fetching new marine weather data for {latitude}, {longitude} from the web.")
    marine_data = fetch_marine_weather_from_web(latitude, longitude)

    if marine_data:
        structured_marine_data = {
            'location': {
                'latitude': latitude,
                'longitude': longitude,
            },
            'current_weather': {
                'sea_temperature': marine_data.get('current_weather', {}).get('sea_surface_temperature'),
                'wave_height': marine_data.get('current_weather', {}).get('wave_height'),
                'wave_direction': marine_data.get('current_weather', {}).get('wave_direction'),
                'current_speed': marine_data.get('current_weather', {}).get('current_speed'),
                'current_direction': marine_data.get('current_weather', {}).get('current_direction'),
            },
        }

        # Update the cache for the specific location
        if cached_data:
            # Update existing cache
            cached_data.data = json.dumps(structured_marine_data)
            cached_data.last_updated = current_time
        else:
            # Insert new cache record
            new_entry = MarineWeatherData(latitude=latitude, longitude=longitude, data=json.dumps(structured_marine_data), last_updated=current_time)
            session.add(new_entry)

        session.commit()

        return structured_marine_data
    else:
        return None
