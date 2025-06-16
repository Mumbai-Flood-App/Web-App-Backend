
# Create your views here.
from .models import AWSStation, StationData, DaywisePrediction, HourlyPrediction, TrainStation
from .serializers import AWSStationSerializer, TrainStationSerializer ,StationDataSerializer, DaywisePredictionSerializer, HourlyPredictionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models.functions import TruncDate, TruncHour
from django.db.models import Sum
from rest_framework import status 
from django.utils.timezone import now, timedelta
import pandas as pd
from django.utils.timezone import make_aware
from datetime import datetime
from django.utils import timezone


class StationListView(APIView):
    def get(self, request):
        stations = AWSStation.objects.all().order_by('name')
        serializer = AWSStationSerializer(stations, many=True)
        return Response(serializer.data)
        # return Response({ 'message': 'Under Construction' }, status=status.HTTP_501_NOT_IMPLEMENTED)
    
class TrainStationListView(APIView):
    def get(self, request):
        stations = TrainStation.objects.all()
        serializer = TrainStationSerializer(stations, many=True)
        return Response(serializer.data)
        # return Response({ 'message': 'Under Construction' }, status=status.HTTP_501_NOT_IMPLEMENTED)

class StationDetailView(APIView):
    def get(self, request, station_id):
        now_time = timezone.now()
        today = now_time.date()
        
        try:
            # Fetch station
            station = AWSStation.objects.get(station_id=station_id)
            serializer = AWSStationSerializer(station).data

            # Get observed data for past 3 days
            three_days_ago = today - timedelta(days=3)
            
            # Create a function to get the start of the rainfall day (11:30 PM previous day)
            def get_rainfall_day_start(date):
                # Convert to IST
                ist = pytz.timezone('Asia/Kolkata')
                start_time = datetime.combine(date - timedelta(days=1), datetime.strptime('23:30', '%H:%M').time())
                return ist.localize(start_time)
            
            # Aggregate data by rainfall day (11:30 PM to 11:30 PM)
            daily_data = []
            current_date = three_days_ago
            while current_date <= today:
                day_start = get_rainfall_day_start(current_date)
                day_end = day_start + timedelta(days=1)
                
                # Get all records for this period
                period_records = StationData.objects.filter(
                    station=station,
                    timestamp__gte=day_start.astimezone(pytz.UTC),  # Convert to UTC for database query
                    timestamp__lt=day_end.astimezone(pytz.UTC)      # Convert to UTC for database query
                ).order_by('timestamp')
                
                # Debug logging
                print(f"\nAnalyzing period for {current_date}:")
                print(f"Start time (IST): {day_start}")
                print(f"End time (IST): {day_end}")
                print(f"Number of records found: {period_records.count()}")
                
                if period_records.exists():
                    first_record = period_records.first()
                    last_record = period_records.last()
                    print(f"First record (UTC): {first_record.timestamp} - {first_record.rainfall}mm")
                    print(f"Last record (UTC): {last_record.timestamp} - {last_record.rainfall}mm")
                
                # Calculate total rainfall
                rainfall = period_records.aggregate(total_rainfall=Sum('rainfall'))['total_rainfall'] or 0
                
                daily_data.append({
                    'date': str(current_date),
                    'total_rainfall': rainfall
                })
                
                current_date += timedelta(days=1)

            # Rest of the code remains the same...
            # Get latest predictions
            pred_daily_data = DaywisePrediction.objects.filter(
                station=station, 
                timestamp__isnull=False
            ).latest('timestamp')

            # Process daily data
            update_daily_data = []
            
            MAX_REASONABLE_RAINFALL = 1000  # mm, adjust as needed

            for data in daily_data:
                pred_date = datetime.strptime(data['date'], '%Y-%m-%d').date() - timedelta(days=1)
                past_prediction = DaywisePrediction.objects.filter(
                    station=station,
                    timestamp__date=pred_date
                ).order_by('-timestamp').first()
            
                predicted_value = past_prediction.day1_rainfall if past_prediction else 0
            
                if predicted_value > MAX_REASONABLE_RAINFALL or predicted_value < 0:
                    print(f"Unreasonable predicted value for {data['date']}: {predicted_value}, setting to 0")
                    predicted_value = 0
            
                update_daily_data.append({
                    'date': str(data['date']),
                    'observed': data['total_rainfall'],
                    'predicted': predicted_value,
                    'is_forecasted': False
                })

            # Add future predictions
            for i in range(1, 4):  # Next 3 days
                future_date = today + timedelta(days=i)
                update_daily_data.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'observed': 0,
                    'predicted': getattr(pred_daily_data, f'day{i}_rainfall', 0),
                    'is_forecasted': True
                })

            # Sort by date to ensure correct order
            update_daily_data.sort(key=lambda x: x['date'])

            return Response({
                'station': serializer,
                'daily_data': update_daily_data,
            })

        except AWSStation.DoesNotExist:
            return Response(
                {'error': 'Station not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error in StationDetailView: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class StationRawDataView(APIView):
    def get(self, request, station_id):
        try:
            station = AWSStation.objects.get(station_id=station_id)
            
            # Get only today's data (24 hours = 96 data points max) (15 minutes data)
            now_time = timezone.now()
            today_start = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            raw_data = StationData.objects.filter(
                station=station, 
                timestamp__gte=today_start,
                timestamp__lte=now_time
            ).order_by('timestamp')
            
            formatted_data = [
                {
                    'timestamp': record.timestamp.isoformat(),
                    'rainfall': record.rainfall
                }
                for record in raw_data
            ]
            
            return Response(formatted_data)
            
        except AWSStation.DoesNotExist:
            return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)
