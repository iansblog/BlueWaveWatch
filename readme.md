# BlueWave Watch

Reporting on water quality, tides and weather for safe river and sea swimming.

## Data Sources and Organizations

Our project utilizes data from the following organizations:

1. [SAS (The Sea Anglers' Society)](http://www.sas.org.uk)
   - SAS is dedicated to promoting sustainable fishing practices and providing valuable insights on sea conditions.

2. [Tide Times](https://www.tidetimes.co.uk)
   - Tide Times offers accurate tidal information, helping users understand sea levels for safe swimming and other water activities.

3. [Open-Meteo](https://api.open-meteo.com)
   - Open-Meteo provides free weather forecasts, enabling users to stay informed about weather conditions at various locations.

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
│   ├── weather_service.py    # Handles weather data fetching and caching
│   ├── tide_service.py       # Manages tide data fetching and caching
│   └── location_service.py   # Fetches location and water quality data
├── models/
│   ├── location_data.py      # SQLAlchemy model for location data
│   ├── tide_data.py          # SQLAlchemy model for tide data
│   └── weather_data.py       # SQLAlchemy model for weather data
├── utils.py              # Utility functions (JSON cleaning, exception handling)
└── README.md                 # Project documentation
```

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

