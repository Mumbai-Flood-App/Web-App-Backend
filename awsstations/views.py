from .models import AWSStation, StationData, DaywisePrediction, HourlyPrediction, TrainStation
from .serializers import AWSStationSerializer, TrainStationSerializer, StationDataSerializer, DaywisePredictionSerializer, HourlyPredictionSerializer
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

class TrainStationListView(APIView):
    def get(self, request):
        stations = TrainStation.objects.all()
        serializer = TrainStationSerializer(stations, many=True)
        return Response(serializer.data)

class StationDetailView(APIView):
    def get(self, request, station_id):
        now_time = timezone.now()
        today = now_time.date()
        
        try:
            # Fetch station
            station = AWSStation.objects.get(station_id=station_id)
            serializer = AWSStationSerializer(station).data

            # Get latest predictions
            pred_daily_data = DaywisePrediction.objects.filter(
                station=station, 
                timestamp__isnull=False
            ).latest('timestamp')

            # Process daily data
            update_daily_data = []
            
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
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StationRawDataView(APIView):
    def get(self, request, station_id):
        try:
            station = AWSStation.objects.get(station_id=station_id)
            
            # Get data for past 3 days
            now_time = timezone.now()
            today = now_time.date()
            three_days_ago = today - timedelta(days=3)
            
            # Create a function to get the start of the rainfall day (11:30 PM previous day)
            def get_rainfall_day_start(date):
                return make_aware(datetime.combine(date - timedelta(days=1), datetime.strptime('23:30', '%H:%M').time()))
            
            # Create a function to get the end of the rainfall day (11:30 PM current day)
            def get_rainfall_day_end(date):
                return make_aware(datetime.combine(date, datetime.strptime('23:30', '%H:%M').time()))
            
            # Get daily aggregated data
            daily_data = []
            current_date = three_days_ago
            
            while current_date <= today:
                day_start = get_rainfall_day_start(current_date)
                day_end = get_rainfall_day_end(current_date)
                
                # Get rainfall for this period
                rainfall = StationData.objects.filter(
                    station=station,
                    timestamp__gte=day_start,
                    timestamp__lt=day_end
                ).aggregate(total_rainfall=Sum('rainfall'))['total_rainfall'] or 0
                
                # Get prediction for this day
                pred_date = current_date - timedelta(days=1)
                past_prediction = DaywisePrediction.objects.filter(
                    station=station,
                    timestamp__date=pred_date
                ).order_by('-timestamp').first()
                
                predicted_value = past_prediction.day1_rainfall if past_prediction else 0
                
                daily_data.append({
                    'date': str(current_date),
                    'observed': rainfall,
                    'predicted': predicted_value,
                    'is_forecasted': False
                })
                
                current_date += timedelta(days=1)
            
            # Sort by date
            daily_data.sort(key=lambda x: x['date'])
            
            return Response({
                'daily_data': daily_data
            })
            
        except AWSStation.DoesNotExist:
            return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)
