# Crowdsource Documentation

## Overview

The Crowdsource module enables community participation in flood monitoring by collecting user-reported flood levels and feedback.

## Models

### CSFormData
- **Purpose**: Stores user-submitted flood reports
- **Fields**:
  - `name`: Name of the reporter (optional)
  - `location`: Description of the location
  - `feedback`: Additional comments or observations
  - `feet`: Water level in feet
  - `inch`: Additional inches of water level
  - `timestamp`: Time of report submission
  - `latitude`: Geographic latitude
  - `longitude`: Geographic longitude

## API Endpoints

### POST /api/crowdsource/report/
Submit a new flood report
- **Required fields**: location, latitude, longitude
- **Optional fields**: name, feedback, feet, inch

### GET /api/crowdsource/reports/
Get all flood reports
- Supports filtering by:
  - Date range
  - Location radius
  - Water level threshold

### GET /api/crowdsource/reports/recent/
Get recent flood reports (last 24 hours)

## Data Validation

1. Location Validation
   - Latitude must be between -90 and 90
   - Longitude must be between -180 and 180
   - Location description required

2. Water Level Validation
   - Feet must be non-negative
   - Inches must be between 0 and 11

3. Timestamp Handling
   - Automatically set to current time
   - Stored in Asia/Kolkata timezone

## Data Usage

The crowdsourced data is used to:
1. Verify automated measurements
2. Fill gaps in sensor coverage
3. Provide ground-truth flood reports
4. Improve flood prediction models
