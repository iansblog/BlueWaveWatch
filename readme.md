# BlueWave Watch

Reporting on water quality, tides and weather for safe river and sea swimming.

## Data Sources and Organisations

Our project utilises data from the following organisations:

* [Surfers Against Sewage](https://www.sas.org.uk) - Surfers Against Sewage is dedicated to protecting the oceans, waves, and beaches by engaging, inspiring, and empowering communities to take action.
    
    **Refresh rate:** This information is refreshed every 60 minutes to keep this site up to date without overwhelming the SAS site.
    
    **Mobile App:** Download the Surfers Against Sewage app for real-time water quality alerts: [Apple](https://apps.apple.com/us/app/surfers-against-sewage/id1065408131) | [Android](https://play.google.com/store/apps/details?id=com.sas.sas&hl=en&gl=US)
    
* [Tide Times](https://www.tidetimes.co.uk) - Tide Times offers accurate tidal information, helping users understand sea levels for safe swimming and other water activities.
    
    **Refresh rate:** This information is refreshed every day per location to keep this site up to date without overwhelming the tidetimes.co.uk site.
    
* [Open-Meteo](https://api.open-meteo.com) - Open-Meteo provides free weather forecasts, enabling users to stay informed about weather conditions at various locations.
    
    **Refresh rate:** This information is refreshed every 60 minutes per location to keep this site up to date without overwhelming the Open-meteo site.
    

We extend our gratitude to these organisations for their valuable data to help ensuring safe swimming conditions.

We extend our gratitude to these organizations for their valuable data and support in ensuring safe swimming conditions.


## Overview

BlueWave Watch is a Python-based application designed to provide real-time weather forecasts, tide data, and water quality information for sea swimmers in the UK, by fetching data from multiple web sources, it helps swimmers make informed decisions about when and where to swim safely.

The application utilises Flask, OpenStreetMap, and web scraping techniques to display relevant data on a map. Users can view the latest weather forecasts, tide times, and water quality information by selecting specific beach locations.

### Features

- **Weather Forecasting:** Fetches up-to-date weather information for any specified location.
- **Tide Times:** Displays current and upcoming tide data based on latitude and longitude.
- **Water Quality Monitoring:** Retrieves water quality data from local agencies to ensure safe swimming conditions.
- **Caching:** Data is cached using an SQLite database to avoid unnecessary API calls and reduce response times.
- **Data Sources:** Information is retrieved from Open-Meteo, Tidetimes.co.uk, and other relevant web services.

## Development Environment

This project uses DevContainers to create a consistent development environment for all contributors. DevContainers are lightweight development environments that can be defined in a `devcontainer.json` file and used within Visual Studio Code.

### Prerequisites

- [Docker](https://www.docker.com/get-started) must be installed.
- [Visual Studio Code](https://code.visualstudio.com/) with the [DevContainers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

### DevContainer Configuration

The development environment is configured using the following `devcontainer.json`:


## Project Structure

```
├── app.py                   # Main Flask application
├── db.py                    # Database setup (engine, session)
├── services/
│   ├── marine_service.py     # Not used at this time as there is no UK data at the moment. 
│   ├── weather_service.py    # Handles weather data fetching and caching
│   ├── tide_service.py       # Manages tide data fetching and caching
│   └── location_service.py   # Fetches location and water quality data
├── models/
│   ├── location_data.py      # SQLAlchemy model for location data
│   ├── tide_data.py          # SQLAlchemy model for tide data
│   └── weather_data.py       # SQLAlchemy model for weather data
├── utils.py                  # Utility functions (JSON cleaning, exception handling)
├── requirements.txt          # Utility functions (JSON cleaning, exception handling)
├── dockerbuild_readme.md     # Just a reminder of how to build and push to docker hub should there be an update. 
├── codeOverview.md           # nn overview of the code flow and DB structure.
└── README.md                 # Project documentation
```

# Project Documentation

This project consists of several important documentation files that provide essential information about the application, its structure, and deployment processes. Below is a brief description of each markdown file available in this repository:

## Documentation Files

- **[dockerbuild_readme.md](dockerbuildReadme.md)**  
  A guide on how to build and push the Docker image to Docker Hub. This document contains instructions for maintaining and updating the Docker setup for the application.

- **[codeOverview.md](codeOverview.md)**  
  An overview of the code flow and database structure. This document provides insights into the architecture of the application, including how different components interact with each other.

- **[readme.md](readme.md)**  
  The main project documentation that outlines the purpose of the project, installation instructions, usage details, and other relevant information for users and developers.

For further details, please refer to the respective markdown files.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/iansblog/BlueWaveWatch.git
   ```

2. Navigate to the project directory:
   ```bash
   cd bluewave-watch
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask application:
   ```bash
   flask run
   ```

## Usage

Once the application is running, you can interact with the map interface, search for specific beaches, and retrieve the latest data regarding tides, weather, and water quality. The app integrates OpenStreetMap to provide a geographical interface for users to interact with.


## Docker 

This project is avalable as a Docker container for you to run, it will run on a Raspbery Pi (tested 5) quite nicly:

- docker run -d -p 80:80 --name bluewavewwatch --restart=always neonsunset/bluewavewwatch

you can run this on any port you would like just change the

- docker run -d -p portNumber:80 --name bluewavewwatch --restart=always neonsunset/bluewavewwatch

You can see the container images on: [https://hub.docker.com/r/neonsunset/bluewavewwatch](https://hub.docker.com/r/neonsunset/bluewavewwatch)

## Example site
This is a running example of the docker container image running in as a subdomain of 26580.co.uk.
(The docker container running)[https://bluewave.26580.co.uk/]
