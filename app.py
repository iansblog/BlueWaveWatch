import json
from db import init_db
from utils import clean_json
init_db()
from flask import Flask, render_template, flash, send_from_directory
from services.ssrs_service import get_SSRS_location_data, get_SSRS_locations
from services.tide_service import fetch_tide_times, create_tide_tables
from services.weather_service import fetch_weather_forecast
from services.marine_service import fetch_marine_weather
from datetime import datetime
import os


app = Flask(__name__)

# Set a secret key for session management.
# This should be a random, unique, and secret value.
app.secret_key = 'your_super_secret_key_here'  # Replace with a strong, unique key

@app.template_filter('date_format')
def date_format(value):
    # Check if value is None or not a string
    if not isinstance(value, str) or value in [None, '', 'Undefined']:
        return "Date not available"  # or return an empty string ""

    try:
        # Convert the string date to a datetime object
        date_obj = datetime.strptime(value, '%Y-%m-%d')
        return date_obj.strftime('%-d %B %Y')  # Format as "1 January 2024"
    except ValueError:
        return value  # If parsing fails, return the original value

@app.route('/')
def index():
    locations = get_SSRS_locations()    
    return render_template('index.html', locations=locations)

# Dynamic route to handle different beach names
@app.route('/location/<beach_name>')
def location(beach_name):
    # Fetching SSRS data
    locations = get_SSRS_locations()    
    # Use the dynamic beach_name in the SSRS location data fetch
    ssrs_data = get_SSRS_location_data(beach_name)

    if 'error' in ssrs_data:
        flash(ssrs_data['error'])
        return render_template('index.html', locations=locations)    

    # Latitude and longitude from SSRS data
    latitude = float(ssrs_data['latitude'])
    longitude = float(ssrs_data['longitude'])

    # Fetching Tide data using the dynamic beach_name
    tide_data = fetch_tide_times(latitude, longitude, beach_name)
    tide_data = clean_json(tide_data)
    tide_data = json.loads(tide_data)

    tideTables = create_tide_tables(tide_data, latitude, longitude)    
    tideTables = clean_json(tideTables)
    tideTables = json.loads(tideTables)
    

    # Fetching Weather Forecast data
    weather_data = fetch_weather_forecast(latitude, longitude)

    # It looks like the marine data is missing for the UK, we will leave this in just in case. 
    # marine_data = fetch_marine_weather(latitude, longitude)

    return render_template(
        'displayBeach.html',
        ssrs_data=ssrs_data,
        tide_data=tide_data,
        weather_data=weather_data,
        latitude=latitude,
        longitude=longitude,
        locations=locations,
        tideTables=tideTables
    )

@app.route('/tidetables/<path:filename>')
def tidetables(filename):
    return  send_from_directory('tidetables', filename)


if __name__ == '__main__':
    app.run(debug=True)
