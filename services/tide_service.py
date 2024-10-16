import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from models import TideTimesData, session
from db import session  # Import the session from db.py

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import os
import re

from scipy.interpolate import CubicSpline

def fetch_tide_times_from_web(lat, lng, beach_name=None):
    url = f'https://www.tidetimes.co.uk/widget?lat={lat}&lng={lng}&days=3&show_distance=true'
    if beach_name:
        url += f'&name={beach_name}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching tide data: {e}")
        return None

def parse_tide_times(html):
    if not html:
        return json.dumps({"error": "No HTML to parse"}, indent=4)

    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find(class_="tidetimes-title").text.strip() if soup.find(class_="tidetimes-title") else "No title found"
    disclaimer = soup.find(class_="tidetimes-disclaimer").text.strip() if soup.find(class_="tidetimes-disclaimer") else "No disclaimer found"
    
    forecasts = []
    forecast_dates = soup.find_all(class_="tidetimes-forecast-date")

    for forecast_date in forecast_dates:
        date_text = forecast_date.text.strip()
        tides_container = forecast_date.find_next('dd', class_="tidetimes-forcast")
        if tides_container:
            tides = tides_container.find_all('dl')
            tides_list = [
                f"{tide.find('dt').text.strip()} at {tide.find('dd').text.strip()}"
                for tide in tides
            ]
            forecasts.append({"date": date_text, "tides": tides_list})

    result = {
        "tidetimes-title": title,
        "tidetimes-disclaimer": disclaimer,
        "forecasts": forecasts if forecasts else "No forecasts found"
    }

    return json.dumps(result, indent=4)

from datetime import datetime, timedelta

def fetch_tide_times(lat, lng, beach_name=None):
    """
    Fetch tide times data based on latitude and longitude. Cache the data and return cached data if it is less than 24 hours old.
    
    Args:
        lat (float): Latitude coordinate.
        lng (float): Longitude coordinate.
        beach_name (str, optional): Optional beach name for fetching tide times.
    
    Returns:
        str: JSON string of the tide data.
    """
    current_time = datetime.now()
    # Query the cache for the specific latitude and longitude
    cached_data = session.query(TideTimesData).filter_by(latitude=lat, longitude=lng).first()

    # Return cached data if it exists and is less than 24 hours old
    if cached_data and current_time - cached_data.last_updated < timedelta(days=1):
        print(f"Returning cached tide times data for {lat}, {lng}.")
        return cached_data.data

    # Fetch new tide times data from the web
    print(f"Fetching new tide times data for {lat}, {lng} from the web.")
    html_response = fetch_tide_times_from_web(lat, lng, beach_name)
    tide_data_json = parse_tide_times(html_response)

    # Update or insert the cache
    if cached_data:
        cached_data.data = tide_data_json
        cached_data.last_updated = current_time
    else:
        new_entry = TideTimesData(latitude=lat, longitude=lng, data=tide_data_json, last_updated=current_time)
        session.add(new_entry)

    # Commit the changes
    session.commit()

    return tide_data_json


def fetch_tide_times_old(lat, lng, beach_name=None):
    current_time = datetime.now()
    cached_data = session.query(TideTimesData).first()

    if cached_data and current_time - cached_data.last_updated < timedelta(minutes=60):
        return cached_data.data

    html_response = fetch_tide_times_from_web(lat, lng, beach_name)
    tide_data_json = parse_tide_times(html_response)

    if cached_data:
        cached_data.data = tide_data_json
        cached_data.last_updated = current_time
    else:
        new_entry = TideTimesData(data=tide_data_json, last_updated=current_time)
        session.add(new_entry)

    session.commit()
    return tide_data_json


# Function to parse time and height from the tide info
def parse_tide(tide_str):
    time_str = tide_str.split(' at ')[-1].split(' ')[0]
    height_str = tide_str.split('(')[-1].replace('m)', '')
    time_obj = datetime.strptime(time_str, '%H:%M')
    height = float(height_str)
    return time_obj, height

from scipy.interpolate import CubicSpline

# Function to create a tide table for a single forecast
def create_tide_table(forecast, latitude, longitude):
    date_str = forecast['date'].replace("Tide Times & Heights for ", "")
    
    # Remove weekday and comma from the date string
    clean_date_str = re.sub(r'Tue, |Wed, |Thu, |Fri, |Sat, |Sun, |Mon, ', '', date_str)  # Remove weekday
    clean_date_str = clean_date_str.replace(',', '')  # Remove comma
    clean_date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', clean_date_str)  # Remove suffixes
    date_obj = datetime.strptime(clean_date_str, '%d %B %Y').date()  # Convert to date object
    
    # Create the filename based on latitude, longitude, and date
    safe_date_str = clean_date_str.replace(' ', '_')  # Format date string for file name
    directory = 'tidetables'  # Directory to store tide table images
    os.makedirs(directory, exist_ok=True)  # Create directory if it doesn't exist
    file_name = os.path.join(directory, f'tide_table_{latitude}_{longitude}_{safe_date_str}.png')
    file_name_only = f'tide_table_{latitude}_{longitude}_{safe_date_str}.png'

    # Check if the file already exists for today
    today = datetime.now().date()
    if date_obj == today:
        # If the file exists, return its name and skip creation
        if os.path.exists(file_name):
            return file_name_only

    # Prepare data for plotting
    times = []
    heights = []
    for tide in forecast['tides']:
        time_obj, height = parse_tide(tide)
        times.append(time_obj.hour + time_obj.minute / 60)  # Convert time to hours
        heights.append(height)

    # Ensure times are strictly increasing by checking for duplicates
    times, heights = zip(*sorted(set(zip(times, heights))))  # Remove duplicates and sort

    # Flatten the curve slightly by reducing the vertical range of heights
    # This can make the plot appear flatter overall
    heights = [height * 0.8 for height in heights]  # Reduce height values slightly for flattening

    # Generate the smooth wave-like curve using cubic spline interpolation
    cubic_spline = CubicSpline(times, heights)
    x = np.linspace(min(times), max(times), 1000)  # Limit x values between the min and max times
    y = cubic_spline(x)  # Generate y-values for the smooth curve

    # Plot the wave and tide points
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='Tide Wave', color='deepskyblue', linewidth=2)

    # Add dashed gray lines for each hour
    for hour in range(25):
        plt.axvline(x=hour, color='lightgray', linestyle='--', linewidth=0.5)  # Dashed line for each hour

    # Plot T-lines for high and low tides
    for i, time in enumerate(times):
        # Draw a vertical T-line for each tide
        plt.vlines(time, 0, heights[i], color='red', linewidth=2)  # Vertical line
        plt.hlines(heights[i], time - 0.2, time + 0.2, color='red', linewidth=2)  # Horizontal top of T-line
        
        # Format time to HH:MM
        formatted_time = datetime.strptime(f"{int(time)}:{int((time % 1) * 60):02d}", "%H:%M").strftime("%H:%M")
        
        # Add both height and time to the plot
        plt.text(time, heights[i] + 0.3, f"{heights[i]:.2f}m\n{formatted_time}", fontsize=10, ha='center', color='black')

    # Highlight tide points with markers
    plt.scatter(times, heights, color='darkblue', s=100, zorder=5)

    # Configure the plot
    plt.title(f'Tide Table - {date_str}', fontsize=14, fontweight='bold')
    plt.xlabel('Time (hours)', fontsize=12)
    plt.ylabel('Tide Height (m)', fontsize=12)
    
    # Set y-ticks to 2m increments for a flatter appearance
    plt.yticks(np.arange(0, max(heights) + 2, 2), fontsize=12, fontweight='bold')

    plt.xticks(np.arange(0, 25, 3), fontsize=12, fontweight='bold')  # Show hours on x-axis
    plt.grid(True, linestyle='--', color='lightgray')
    plt.ylim(0, max(heights) + 2)  # Scale y-axis for tide heights

    # Add legend at the top left
    plt.legend(['Tide Wave', 'High/Low Tides'], loc='upper left')

    # Save the plot
    plt.savefig(file_name)
    plt.close()  # Close the plot to avoid displaying it immediately
    
    return file_name_only  # Return the name of the created file

# Function to create a tide table for a single forecast
def create_tide_table_oldschool3(forecast, latitude, longitude):
    date_str = forecast['date'].replace("Tide Times & Heights for ", "")
    
    # Remove weekday and comma from the date string
    clean_date_str = re.sub(r'Tue, |Wed, |Thu, |Fri, |Sat, |Sun, |Mon, ', '', date_str)  # Remove weekday
    clean_date_str = clean_date_str.replace(',', '')  # Remove comma
    clean_date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', clean_date_str)  # Remove suffixes
    date_obj = datetime.strptime(clean_date_str, '%d %B %Y').date()  # Convert to date object
    
    # Create the filename based on latitude, longitude, and date
    safe_date_str = clean_date_str.replace(' ', '_')  # Format date string for file name
    directory = 'tidetables'  # Directory to store tide table images
    os.makedirs(directory, exist_ok=True)  # Create directory if it doesn't exist
    file_name = os.path.join(directory, f'tide_table_{latitude}_{longitude}_{safe_date_str}.png')
    file_name_only = f'tide_table_{latitude}_{longitude}_{safe_date_str}.png'

    # Check if the file already exists for today
    today = datetime.now().date()
    if date_obj == today:
        # If the file exists, return its name and skip creation
        if os.path.exists(file_name):
            return file_name_only

    # Prepare data for plotting
    times = []
    heights = []
    for tide in forecast['tides']:
        time_obj, height = parse_tide(tide)
        times.append(time_obj.hour + time_obj.minute / 60)  # Convert time to hours
        heights.append(height)

    # Generate the wave-like curve to align with actual tide points
    x = np.linspace(0, 24, 1000)
    y = np.interp(x, times, heights)  # Interpolates between high/low tide points for a smooth wave

    # Plot the wave and tide points
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='Tide Wave', color='deepskyblue', linewidth=2)

    # Add dashed gray lines for each hour
    for hour in range(25):
        plt.axvline(x=hour, color='lightgray', linestyle='--', linewidth=0.5)  # Dashed line for each hour

    # Plot T-lines for high and low tides
    for i, time in enumerate(times):
        # Draw a vertical T-line for each tide
        plt.vlines(time, 0, heights[i], color='red', linewidth=2)  # Vertical line
        plt.hlines(heights[i], time - 0.2, time + 0.2, color='red', linewidth=2)  # Horizontal top of T-line
        
        # Format time to HH:MM
        formatted_time = datetime.strptime(f"{int(time)}:{int((time % 1) * 60):02d}", "%H:%M").strftime("%H:%M")
        
        # Add both height and time to the plot
        plt.text(time, heights[i] + 0.3, f"{heights[i]:.2f}m\n{formatted_time}", fontsize=10, ha='center', color='black')

    # Highlight tide points with markers
    plt.scatter(times, heights, color='darkblue', s=100, zorder=5)

    # Configure the plot
    plt.title(f'Tide Table - {date_str}', fontsize=14, fontweight='bold')
    plt.xlabel('Time (hours)', fontsize=12)
    plt.ylabel('Tide Height (m)', fontsize=12)
    plt.xticks(np.arange(0, 25, 3), fontsize=12, fontweight='bold')  # Show hours on x-axis
    plt.grid(True, linestyle='--', color='lightgray')
    plt.ylim(0, max(heights) + 1)  # Scale y-axis for tide heights

    # Add legend at the top left
    plt.legend(['Tide Wave', 'High/Low Tides'], loc='upper left')

    # Save the plot
    plt.savefig(file_name)
    plt.close()  # Close the plot to avoid displaying it immediately
    
    return file_name_only  # Return the name of the created file


# Function to create a tide table for a single forecast
def create_tide_table_oldschool2(forecast, latitude, longitude):
    date_str = forecast['date'].replace("Tide Times & Heights for ", "")
    
    # Remove weekday and comma from the date string
    clean_date_str = re.sub(r'Tue, |Wed, |Thu, |Fri, |Sat, |Sun, |Mon, ', '', date_str)  # Remove weekday
    clean_date_str = clean_date_str.replace(',', '')  # Remove comma
    clean_date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', clean_date_str)  # Remove suffixes
    date_obj = datetime.strptime(clean_date_str, '%d %B %Y').date()  # Convert to date object
    
    # Create the filename based on latitude, longitude, and date
    safe_date_str = clean_date_str.replace(' ', '_')  # Format date string for file name
    directory = 'tidetables'  # Directory to store tide table images
    os.makedirs(directory, exist_ok=True)  # Create directory if it doesn't exist
    file_name = os.path.join(directory, f'tide_table_{latitude}_{longitude}_{safe_date_str}.png')
    file_name_only = f'tide_table_{latitude}_{longitude}_{safe_date_str}.png'

    # Check if the file already exists for today
    today = datetime.now().date()
    if date_obj == today:
        # If the file exists, return its name and skip creation
        if os.path.exists(file_name):
            return file_name_only

    # Prepare data for plotting
    times = []
    heights = []
    for tide in forecast['tides']:
        time_obj, height = parse_tide(tide)
        times.append(time_obj.hour + time_obj.minute / 60)  # Convert time to hours
        heights.append(height)

    # Generate the wave-like curve to align with actual tide points
    x = np.linspace(0, 24, 1000)
    y = np.interp(x, times, heights)  # Interpolates between high/low tide points for a smooth wave

    # Plot the wave and tide points
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='Tide Wave', color='deepskyblue', linewidth=2)

    # Add dashed gray lines for each hour
    for hour in range(25):
        plt.axvline(x=hour, color='lightgray', linestyle='--', linewidth=0.5)  # Dashed line for each hour

    # Plot T-lines for high and low tides
    for i, time in enumerate(times):
        # Draw a vertical T-line for each tide
        plt.vlines(time, 0, heights[i], color='red', linewidth=2)  # Vertical line
        plt.hlines(heights[i], time - 0.2, time + 0.2, color='red', linewidth=2)  # Horizontal top of T-line
        plt.text(time, heights[i] + 0.3, f"{heights[i]:.2f}m", fontsize=12, ha='center', color='black')

    # Highlight tide points with markers
    plt.scatter(times, heights, color='darkblue', s=100, zorder=5)

    # Configure the plot
    plt.title(f'Tide Table - {date_str}', fontsize=14, fontweight='bold')
    plt.xlabel('Time (hours)', fontsize=12)
    plt.ylabel('Tide Height (m)', fontsize=12)
    plt.xticks(np.arange(0, 25, 3), fontsize=12, fontweight='bold')  # Show hours on x-axis
    plt.grid(True, linestyle='--', color='lightgray')
    plt.ylim(0, max(heights) + 1)  # Scale y-axis for tide heights

    # Add legend
    plt.legend(['Tide Wave', 'High/Low Tides'], loc='upper right')

    # Save the plot
    plt.savefig(file_name)
    plt.close()  # Close the plot to avoid displaying it immediately
    
    return file_name_only  # Return the name of the created file


# Function to create a tide table for a single forecast
def create_tide_table_oldschool(forecast, latitude, longitude):
    date_str = forecast['date'].replace("Tide Times & Heights for ", "")
    
    # Remove weekday and comma from the date string
    clean_date_str = re.sub(r'Tue, |Wed, |Thu, |Fri, |Sat, |Sun, |Mon, ', '', date_str)  # Remove weekday
    clean_date_str = clean_date_str.replace(',', '')  # Remove comma
    clean_date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', clean_date_str)  # Remove suffixes
    date_obj = datetime.strptime(clean_date_str, '%d %B %Y').date()  # Convert to date object
    
    # Create the filename based on latitude, longitude, and date
    safe_date_str = clean_date_str.replace(' ', '_')  # Format date string for file name
    directory = 'tidetables'  # Directory to store tide table images
    os.makedirs(directory, exist_ok=True)  # Create directory if it doesn't exist
    file_name = os.path.join(directory, f'tide_table_{latitude}_{longitude}_{safe_date_str}.png')
    file_name_only = f'tide_table_{latitude}_{longitude}_{safe_date_str}.png'

    # Check if the file already exists for today
    today = datetime.now().date()
    if date_obj == today:
        # If the file exists, return its name and skip creation
        if os.path.exists(file_name):
            return file_name_only

    # Prepare data for plotting
    times = []
    heights = []
    for tide in forecast['tides']:
        time_obj, height = parse_tide(tide)
        times.append(time_obj.hour + time_obj.minute / 60)  # Convert time to hours
        heights.append(height)

    # Generate the wave-like curve to align with actual tide points
    x = np.linspace(0, 24, 1000)
    y = np.interp(x, times, heights)  # Interpolates between high/low tide points for a smooth wave

    # Plot the wave and tide points
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='Tide Wave', color='lightblue')

    # Add dashed gray lines for each hour
    for hour in range(25):
        plt.axvline(x=hour, color='gray', linestyle='--', linewidth=0.5)  # Dashed line for each hour

    # Plot T-lines for high and low tides
    for i, time in enumerate(times):
        # Draw a vertical T-line for each tide
        plt.vlines(time, 0, heights[i], color='red', linewidth=2)  # Vertical line
        plt.hlines(heights[i], time - 0.2, time + 0.2, color='red', linewidth=2)  # Horizontal top of T-line
        plt.text(time, heights[i] + 0.3, f"{heights[i]:.2f}m", fontsize=10, ha='center')

    # Configure the plot
    plt.title(f'Tide Table - {date_str}')
    plt.xlabel('Time (hours)')
    plt.ylabel('Tide Height (m)')
    plt.xticks(np.arange(0, 25, 3))  # Show hours on x-axis
    plt.grid(True)
    plt.ylim(0, max(heights) + 1)  # Scale y-axis for tide heights

    # Save the plot
    plt.savefig(file_name)
    plt.close()  # Close the plot to avoid displaying it immediately
    
    return file_name_only  # Return the name of the created file

# Function to delete old tide table files
def delete_old_files(directory):
    today = datetime.now().date()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # Check if it's a file and if it's older than today
        if os.path.isfile(file_path):
            file_creation_date = datetime.fromtimestamp(os.path.getctime(file_path)).date()
            if file_creation_date < today:
                os.remove(file_path)  # Delete the file
                print(f'Deleted old file: {file_path}')

# Function to create tide tables for each day
def create_tide_tables(tide_data, latitude, longitude):
    directory = 'tidetables'  # Directory to store tide table images
    os.makedirs(directory, exist_ok=True)  # Create directory if it doesn't exist
    delete_old_files(directory)  # Delete files created before today
    existing_files = []

    for forecast in tide_data['forecasts']:
        file_name = create_tide_table(forecast, latitude, longitude)  # Create a tide table for the forecast
        existing_files.append(file_name)  # Add the file name to the list of existing files

    # Return JSON array of all files created or already existing
    return json.dumps(existing_files)
