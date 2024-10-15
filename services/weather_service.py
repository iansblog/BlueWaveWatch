import requests
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from models import WeatherForecastData  # Assuming you have a models.py file for your ORM classes
from db import session  # Import the session from db.py

def get_wind_direction(degrees):
    directions = ['North', 'North-East', 'East', 'South-East', 'South', 'South-West', 'West', 'North-West']
    idx = round(degrees / 45) % 8
    return directions[idx]

def get_weather_description(weather_code):
    if weather_code == 0:
        return "Clear Sky"
    elif weather_code == 1:
        return "Partly Cloudy"
    elif weather_code == 2:
        return "Cloudy"
    elif weather_code >= 3:
        return "Rainy"
    elif weather_code == 71 or weather_code == 85:
        return "Snowing"
    # Add more mappings if needed
    return "Unknown"


def fetch_weather_forecast_from_web(latitude, longitude):
    """
    Fetch weather forecast from the Open-Meteo API for given latitude and longitude.
    
    Args:
        latitude (float): Latitude coordinate.
        longitude (float): Longitude coordinate.

    Returns:
        dict: A dictionary containing weather forecast information.
    """
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": "true",
        "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,windspeed_10m_max,winddirection_10m_dominant",
        "timezone": "auto",
        "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,windspeed_10m_max,winddirection_10m_dominant",  # Specify the weather data you want
        "days": 3  # Add this line to specify you want data for 3 days
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def fetch_weather_forecast_old(latitude, longitude):
    """
    Check if the weather forecast data exists in the cache and is less than 60 minutes old.
    If not, fetch new data from the web and update the cache.

    Args:
        latitude (float): Latitude coordinate.
        longitude (float): Longitude coordinate.

    Returns:
        dict: A dictionary containing structured weather forecast information.
    """
    current_time = datetime.now()
    cached_data = session.query(WeatherForecastData).first()

    # If data is recent, return cached data
    if cached_data and current_time - cached_data.last_updated < timedelta(minutes=60):
        print("Returning cached weather forecast data.")
        return json.loads(cached_data.data)

    # Otherwise, fetch new data
    print("Fetching new weather forecast data from the web.")
    forecast_data = fetch_weather_forecast_from_web(latitude, longitude)

    if forecast_data:
        # Structure the weather data for the template
        structured_weather_data = {
            'location': {
                'latitude': latitude,
                'longitude': longitude,
            },
            'current_weather': {
                'temperature': forecast_data.get('current_weather', {}).get('temperature'),
                'weather_code': forecast_data.get('current_weather', {}).get('weathercode'),
                'wind_speed': forecast_data.get('current_weather', {}).get('windspeed'),
                'wind_direction': forecast_data.get('current_weather', {}).get('winddirection'),
                'weather_description': get_weather_description(forecast_data.get('current_weather', {}).get('weathercode'))  
            },
            'forecast': {  # Added the 'forecast' key here
                'day_1': {
                    'max_temp': forecast_data.get('daily', {}).get('temperature_2m_max', [])[0],
                    'min_temp': forecast_data.get('daily', {}).get('temperature_2m_min', [])[0],
                    'sunrise': forecast_data.get('daily', {}).get('sunrise', [])[0],
                    'sunset': forecast_data.get('daily', {}).get('sunset', [])[0],
                    'precipitation': forecast_data.get('daily', {}).get('precipitation_sum', [])[0],
                    'wind_speed': forecast_data.get('daily', {}).get('windspeed_10m_max', [])[0],
                    'wind_direction': forecast_data.get('daily', {}).get('winddirection_10m_dominant', [])[0],
                    'wind_direction_text': get_wind_direction(forecast_data.get('daily', {}).get('winddirection_10m_dominant', [])[0]),
                    'formatted_date': datetime.fromisoformat(forecast_data.get('daily', {}).get('sunrise', [])[0]).strftime("%d %B %Y"),
                    'weather_description': get_weather_description(forecast_data.get('current_weather', {}).get('weathercode'))  
                },
                'day_2': {
                    'max_temp': forecast_data.get('daily', {}).get('temperature_2m_max', [])[1],
                    'min_temp': forecast_data.get('daily', {}).get('temperature_2m_min', [])[1],
                    'sunrise': forecast_data.get('daily', {}).get('sunrise', [])[1],
                    'sunset': forecast_data.get('daily', {}).get('sunset', [])[1],
                    'precipitation': forecast_data.get('daily', {}).get('precipitation_sum', [])[1],
                    'wind_speed': forecast_data.get('daily', {}).get('windspeed_10m_max', [])[1],
                    'wind_direction': forecast_data.get('daily', {}).get('winddirection_10m_dominant', [])[1],
                    'wind_direction_text': get_wind_direction(forecast_data.get('daily', {}).get('winddirection_10m_dominant', [])[1]),
                    'formatted_date': datetime.fromisoformat(forecast_data.get('daily', {}).get('sunrise', [])[1]).strftime("%d %B %Y"),
                    'weather_description': get_weather_description(forecast_data.get('current_weather', {}).get('weathercode'))  
                }

            }
        }

        # Update the cache
        if cached_data:
            # Update existing cache
            cached_data.data = json.dumps(structured_weather_data)
            cached_data.last_updated = current_time
        else:
            # Insert new cache record
            new_entry = WeatherForecastData(data=json.dumps(structured_weather_data), last_updated=current_time)
            session.add(new_entry)

        session.commit()

        return structured_weather_data
    else:
        return None

def fetch_weather_forecast(latitude, longitude):
    """
    Check if the weather forecast data exists in the cache for the specific location and is less than 60 minutes old.
    If not, fetch new data from the web and update the cache.

    Args:
        latitude (float): Latitude coordinate.
        longitude (float): Longitude coordinate.

    Returns:
        dict: A dictionary containing structured weather forecast information.
    """
    current_time = datetime.now()

    # Query the database for cached data for the specific latitude and longitude
    cached_data = session.query(WeatherForecastData).filter_by(latitude=latitude, longitude=longitude).first()

    # If data exists and is less than 60 minutes old, return cached data
    if cached_data and current_time - cached_data.last_updated < timedelta(minutes=60):
        print(f"Returning cached weather forecast data for {latitude}, {longitude}.")
        return json.loads(cached_data.data)

    # Otherwise, fetch new data
    print(f"Fetching new weather forecast data for {latitude}, {longitude} from the web.")
    forecast_data = fetch_weather_forecast_from_web(latitude, longitude)

    if forecast_data:
        # Structure the weather data for the template
        structured_weather_data = {
            'location': {
                'latitude': latitude,
                'longitude': longitude,
            },
            'current_weather': {
                'temperature': forecast_data.get('current_weather', {}).get('temperature'),
                'weather_code': forecast_data.get('current_weather', {}).get('weathercode'),
                'wind_speed': forecast_data.get('current_weather', {}).get('windspeed'),
                'wind_direction': forecast_data.get('current_weather', {}).get('winddirection'),
                'weather_description': get_weather_description(forecast_data.get('current_weather', {}).get('weathercode'))  
            },
            'forecast': {  # Added the 'forecast' key here
                'day_1': {
                    'max_temp': forecast_data.get('daily', {}).get('temperature_2m_max', [])[0],
                    'min_temp': forecast_data.get('daily', {}).get('temperature_2m_min', [])[0],
                    'sunrise': forecast_data.get('daily', {}).get('sunrise', [])[0],
                    'sunset': forecast_data.get('daily', {}).get('sunset', [])[0],
                    'precipitation': forecast_data.get('daily', {}).get('precipitation_sum', [])[0],
                    'wind_speed': forecast_data.get('daily', {}).get('windspeed_10m_max', [])[0],
                    'wind_direction': forecast_data.get('daily', {}).get('winddirection_10m_dominant', [])[0],
                    'wind_direction_text': get_wind_direction(forecast_data.get('daily', {}).get('winddirection_10m_dominant', [])[0]),
                    'formatted_date': datetime.fromisoformat(forecast_data.get('daily', {}).get('sunrise', [])[0]).strftime("%d %B %Y"),
                    'weather_description': get_weather_description(forecast_data.get('current_weather', {}).get('weathercode'))  
                },
                'day_2': {
                    'max_temp': forecast_data.get('daily', {}).get('temperature_2m_max', [])[1],
                    'min_temp': forecast_data.get('daily', {}).get('temperature_2m_min', [])[1],
                    'sunrise': forecast_data.get('daily', {}).get('sunrise', [])[1],
                    'sunset': forecast_data.get('daily', {}).get('sunset', [])[1],
                    'precipitation': forecast_data.get('daily', {}).get('precipitation_sum', [])[1],
                    'wind_speed': forecast_data.get('daily', {}).get('windspeed_10m_max', [])[1],
                    'wind_direction': forecast_data.get('daily', {}).get('winddirection_10m_dominant', [])[1],
                    'wind_direction_text': get_wind_direction(forecast_data.get('daily', {}).get('winddirection_10m_dominant', [])[1]),
                    'formatted_date': datetime.fromisoformat(forecast_data.get('daily', {}).get('sunrise', [])[1]).strftime("%d %B %Y"),
                    'weather_description': get_weather_description(forecast_data.get('current_weather', {}).get('weathercode'))  
                }

            }
        }

        # Update the cache for the specific location
        if cached_data:
            # Update existing cache
            cached_data.data = json.dumps(structured_weather_data)
            cached_data.last_updated = current_time
        else:
            # Insert new cache record
            new_entry = WeatherForecastData(latitude=latitude, longitude=longitude, data=json.dumps(structured_weather_data), last_updated=current_time)
            session.add(new_entry)

        session.commit()

        return structured_weather_data
    else:
        return None
