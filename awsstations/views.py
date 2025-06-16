
# Create your views here.
from .models import AWSStation, StationData, DaywisePrediction, HourlyPrediction, TrainStation
from .serializers import AWSStationSerializer, TrainStationSerializer ,StationDataSerializer, DaywisePredictionSerializer, HourlyPredictionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models.functions import TruncDate, TruncHour, TruncMinute
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

            # Get observed data for past 3 days with 15-minute intervals
            three_days_ago = today - timedelta(days=3)
            raw_data = (
                StationData.objects
                .filter(
                    station=station, 
                    timestamp__gte=three_days_ago, 
                    timestamp__lte=now_time
                )
                .annotate(
                    date=TruncDate('timestamp')
                )
                .values('date')
                .annotate(total_rainfall=Sum('rainfall'))
                .order_by('date')
            )

            # Convert to dictionary for easier lookup
            daily_sums = {
                data['date'].strftime('%Y-%m-%d'): data['total_rainfall']
                for data in raw_data
            }

            # Get latest predictions
            pred_daily_data = DaywisePrediction.objects.filter(
                station=station, 
                timestamp__isnull=False
            ).latest('timestamp')

            # Process daily data
            update_daily_data = []
            
            MAX_REASONABLE_RAINFALL = 1000  # mm, adjust as needed

            # Add observed data with past predictions
            for date_str, total_rainfall in daily_sums.items():
                # Convert string date to timezone-aware datetime
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                pred_date = date_obj - timedelta(days=1)
                
                past_prediction = DaywisePrediction.objects.filter(
                    station=station,
                    timestamp__date=pred_date
                ).order_by('-timestamp').first()
            
                predicted_value = past_prediction.day1_rainfall if past_prediction else 0
            
                # Debug print
                print(f"Observed date: {date_str}, pred_date: {pred_date}, predicted_value: {predicted_value}")
            
                if predicted_value > MAX_REASONABLE_RAINFALL or predicted_value < 0:
                    print(f"Unreasonable predicted value for {date_str}: {predicted_value}, setting to 0")
                    predicted_value = 0
            
                update_daily_data.append({
                    'date': date_str,
                    'observed': total_rainfall,
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
                'daily_data': update_daily_data
            })

        except AWSStation.DoesNotExist:
            return Response(
                {'error': 'Station not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error in StationDetailView: {str(e)}")  # Add this for debugging
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
