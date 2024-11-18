# Weather Stations Documentation

## Overview

The Weather Stations module manages physical weather monitoring stations that track water levels. Each station can have an associated image for visual monitoring.

## Models

### WeatherStation
- **Purpose**: Represents a physical weather monitoring station
- **Fields**:
  - `name`: Station name
  - `latitude`: Geographic latitude
  - `longitude`: Geographic longitude
  - `image`: Optional image of the station
  - `curr_waterlevel`: Current water level reading

### Waterlevel_Data
- **Purpose**: Historical water level data for each station
- **Fields**:
  - `station`: Foreign key to WeatherStation
  - `waterlevel`: Water level measurement
  - `timestamp`: Time of measurement

## API Endpoints

### GET /api/weather/stations/
Lists all weather stations with their current water levels

### GET /api/weather/stations/{id}/
Retrieves detailed information for a specific station

### GET /api/weather/waterlevels/
Gets historical water level data for all stations

### GET /api/weather/waterlevels/{station_id}/
Gets historical water level data for a specific station

## Data Flow

1. Weather stations report water level readings
2. Data is stored in Waterlevel_Data model
3. Current water level is updated in WeatherStation model
4. API endpoints provide access to current and historical data

## Image Management

- Station images are stored in 'weatherstation_images/' directory
- Images help in visual verification of water levels
- Supported formats: JPEG, PNG
- Maximum file size: 5MB
