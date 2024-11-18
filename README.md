# ClimateBackend

A comprehensive backend service for climate data processing, analysis, and prediction. This system integrates data from multiple sources including automated weather stations (AWS), weather stations, and crowdsourced information to provide accurate climate insights.

## Features

- **AWS Station Management**
  - Track rainfall data from automated weather stations
  - Store and manage station information
  - Provide daily and hourly rainfall predictions
  - Monitor train station warnings based on rainfall data

- **Weather Station Monitoring**
  - Track water levels at various weather stations
  - Store historical water level data
  - Visual monitoring through station images

- **Crowdsource Data Collection**
  - Collect user-reported flood levels
  - Gather location-based feedback
  - Community-driven flood monitoring

- **Database Middleware**
  - Centralized data access layer
  - Data validation and processing
  - Cross-source data integration

- **Data Dashboard**
  - Unified data visualization interface
  - Server-side filtering and processing
  - Multi-source data integration
  - Data export capabilities

## Project Structure

```
ClimateBackend/
├── awsstations/        # AWS station data management
├── weatherstations/    # Weather station monitoring
├── crowdsource/       # Crowdsourced data collection
├── dbmiddlelayer/     # Database abstraction layer
├── dashboard/         # Data visualization interface
├── docs/             # Project documentation
└── server/           # Core Django settings
```

## Technology Stack

- **Framework**: Django 5.1.3
- **Database**: PostgreSQL
- **Task Queue**: Celery 5.4.0
- **Machine Learning**: TensorFlow 2.18.0
- **API**: Django REST Framework 3.15.2

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ClimateBackend.git
cd ClimateBackend
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## API Documentation

### AWS Stations

- `GET /aws/stations/` - List all AWS stations
- `GET /aws/stations/<id>/` - Get specific station details
- `GET /aws/predictions/` - Get rainfall predictions

### Weather Stations

- `GET /weather/stations/` - List all weather stations
- `GET /weather/waterlevels/` - Get current water levels

### Crowdsource

- `POST /cs/report/` - Submit a flood report
- `GET /cs/reports/` - Get all flood reports

### Database Middleware

- `GET /db/health/` - Check system health
- Various internal endpoints for data integration

## Environment Variables

Required environment variables:

```env
# Django settings
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Static files
STATIC_URL=/static/
MEDIA_URL=/media/
```

## Documentation

Detailed documentation is available in the `docs/` directory:

- [AWS Stations Documentation](docs/aws_stations.md)
- [Weather Stations Documentation](docs/weather_stations.md)
- [Crowdsource Documentation](docs/crowdsource.md)
- [Dashboard Documentation](docs/dashboard.md)
- [Architecture Overview](docs/architecture.md)

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers directly.
