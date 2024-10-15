import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta
from models import SSRSLocationData, session
from utils import clean_json
from db import session  # Import the session from db.py
from flask import jsonify

SSRSurl = "https://www.securetransaction.uk/sas/map/map-code.php"


def SSRS_fetch_location_data_from_web():
    try:
        response = requests.get(SSRSurl, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        load_markers_script = soup.find("script", text=re.compile("function LoadMarkers()"))
        if not load_markers_script:
            return json.dumps({"error": "LoadMarkers function not found in the HTML."}, indent=4)

        load_markers_content = load_markers_script.string
        location_pattern = re.compile(
            r"<div style=\"min-width:300px; max-width:350px;\">(.*?)<br>(.*?)<br>(.*?)<br>.*?LatLng\((.*?),\s(.*?)\);",
            re.DOTALL
        )
        matches = location_pattern.findall(load_markers_content)

        if not matches:
            return json.dumps({"error": "No matching locations found in LoadMarkers."}, indent=4)

        locations = [
            {
                "Location": match[0].replace("'; \n contentString = contentString + '", "").strip(),
                "Status": match[1].replace("'; \n  contentString = contentString + '", "").strip(),
                "LocationDescription": match[2].replace("'; \n contentString = contentString + '", "").strip(),
                "latitude": match[3].strip(),
                "longitude": match[4].strip()
            }
            for match in matches
        ]
        return json.dumps(locations, indent=4)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=4)

def SSRS_fetch_location_data(url):
    try:
        cached_data = session.query(SSRSLocationData).first()
        current_time = datetime.now()

        if cached_data and current_time - cached_data.last_updated < timedelta(minutes=60):
            return cached_data.data

        new_data = SSRS_fetch_location_data_from_web()
        
        if isinstance(new_data, dict) and 'error' in new_data:
            # If new_data contains an error, return it directly without saving
            return new_data
        
        if cached_data:
            cached_data.data = new_data
            cached_data.last_updated = current_time
        else:
            new_entry = SSRSLocationData(data=new_data, last_updated=current_time)
            session.add(new_entry)
        
        session.commit()
        return new_data
    
    except Exception as e:
        return json.dumps({"error": f"Database error: {str(e)}"}, indent=4)

def SSRS_get_location_data(locationResultjSon, location):
    try:
        for loc in locationResultjSon:
            if loc["Location"] == location:
                return loc
        return {"error": "Location not found."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def get_SSRS_location_data(SSRSLocation):

    SSRSLocationResultjSon = SSRS_fetch_location_data(SSRSurl)
    SSRSLocationResultjSon = clean_json(SSRSLocationResultjSon)

    try:
        SSRSLocationResultjSon = json.loads(SSRSLocationResultjSon)
        SSRSjSon = SSRS_get_location_data(SSRSLocationResultjSon, SSRSLocation)
        return SSRSjSon
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON data."}

import json
from flask import jsonify

def get_SSRS_locations():
    SSRSLocationResultjSon = SSRS_fetch_location_data(SSRSurl)
    SSRSLocationResultjSon = clean_json(SSRSLocationResultjSon)

    try:
        # Load the cleaned JSON string into a Python list or dict
        SSRSLocationResultjSon = json.loads(SSRSLocationResultjSon)
        
        # Extract location data
        locations = [{"Location": entry["Location"]} for entry in SSRSLocationResultjSon]
        
        # Return the locations as a JSON response
        return locations
        #return jsonify(locations)
    
    except json.JSONDecodeError as jde:
        # Handle JSON decoding errors specifically
        return json.dumps({"error": f"JSON decoding error: {str(jde)}"})
    
    except Exception as e:
        # Return a general error message as a JSON string
        return json.dumps({"error": f"Unexpected error: {str(e)}"})
