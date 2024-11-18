# AWS Stations Documentation

## Overview

The AWS Stations module manages automated weather stations and their data. It tracks rainfall measurements, provides predictions, and monitors train station warnings.

## Models

### AWSStation
- **Purpose**: Represents an automated weather station
- **Fields**:
  - `station_id`: Unique identifier for the station
  - `name`: Station name
  - `latitude`: Geographic latitude
  - `longitude`: Geographic longitude
  - `rainfall`: Current rainfall measurement

### StationData
- **Purpose**: Historical rainfall data for each station
- **Fields**:
  - `station`: Foreign key to AWSStation
  - `rainfall`: Rainfall measurement
  - `timestamp`: Time of measurement

### DaywisePrediction
- **Purpose**: Stores 3-day rainfall predictions
- **Fields**:
  - `station`: Associated AWS station
  - `timestamp`: Prediction time
  - `day1_rainfall`: Predicted rainfall for day 1
  - `day2_rainfall`: Predicted rainfall for day 2
  - `day3_rainfall`: Predicted rainfall for day 3

### HourlyPrediction
- **Purpose**: Stores 24-hour rainfall predictions
- **Fields**:
  - `station`: Associated AWS station
  - `timestamp`: Prediction time
  - `hr_24_rainfall`: JSON field with hourly predictions

### TrainStation
- **Purpose**: Links train stations to nearest AWS stations
- **Fields**:
  - `station_code`: Unique train station identifier
  - `station_name`: Name of the train station
  - `latitude`: Geographic latitude
  - `longitude`: Geographic longitude
  - `neareststation`: Link to nearest AWS station
  - `WarningLevel`: Current warning level (0-3)

## API Endpoints

### GET /api/aws/stations/
Lists all AWS stations with their current rainfall data

### GET /api/aws/stations/{id}/
Retrieves detailed information for a specific station

### GET /api/aws/predictions/daily/
Gets 3-day rainfall predictions for all stations

### GET /api/aws/predictions/hourly/
Gets 24-hour rainfall predictions for all stations

### GET /api/aws/warnings/
Lists all train stations with their current warning levels

## Data Flow

1. AWS stations continuously send rainfall data
2. Data is stored in StationData model
3. ML models generate predictions
4. Warning levels are updated based on rainfall and predictions
5. Train stations are notified of warning levels
