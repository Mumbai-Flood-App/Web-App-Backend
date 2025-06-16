
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
import pytz
from collections import defaultdict


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
        print("=== STATION DETAIL VIEW CODE IS LIVE ===")
        now_time = timezone.now()
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = now_time.astimezone(ist)
        today_ist = now_ist.date()
        three_days_ago_ist = today_ist - timedelta(days=3)
        start_dt_ist = ist.localize(datetime.combine(three_days_ago_ist, datetime.min.time()))
        end_dt_ist = ist.localize(datetime.combine(today_ist, datetime.max.time()))

        try:
            # Fetch station
            station = AWSStation.objects.get(station_id=station_id)
            serializer = AWSStationSerializer(station).data

            # Fetch all records in the IST range
            records = StationData.objects.filter(
                station=station,
                timestamp__gte=start_dt_ist,
                timestamp__lte=end_dt_ist
            ).order_by('timestamp')

            # Aggregate in Python by IST date
            daily_totals = defaultdict(float)
            for rec in records:
                rec_ist = rec.timestamp.astimezone(ist)
                date_str = rec_ist.strftime('%Y-%m-%d')
                daily_totals[date_str] += rec.rainfall

            # Debug: print daily sums
            print("=== DEBUG: StationDetailView (daily_totals) ===")
            for date_str in sorted(daily_totals.keys()):
                print(f"Date: {date_str}, Total rainfall: {daily_totals[date_str]}")
            print("=== END DEBUG ===")

            # Get latest predictions
            pred_daily_data = DaywisePrediction.objects.filter(
                station=station, 
                timestamp__isnull=False
            ).latest('timestamp')

            # Build daily_data for the last 4 days
            update_daily_data = []
            MAX_REASONABLE_RAINFALL = 1000  # mm, adjust as needed

            for i in range(4):
                day = three_days_ago_ist + timedelta(days=i)
                date_str = day.strftime('%Y-%m-%d')
                observed = daily_totals.get(date_str, 0)

                # Get prediction for this day
                pred_date = day - timedelta(days=1)
                past_prediction = DaywisePrediction.objects.filter(
                    station=station,
                    timestamp__date=pred_date
                ).order_by('-timestamp').first()
                predicted_value = past_prediction.day1_rainfall if past_prediction else 0
                if predicted_value > MAX_REASONABLE_RAINFALL or predicted_value < 0:
                    predicted_value = 0

                update_daily_data.append({
                    'date': date_str,
                    'observed': observed,
                    'predicted': predicted_value,
                    'is_forecasted': False
                })

            # Add future predictions (next 3 days)
            for i in range(1, 4):
                future_date = today_ist + timedelta(days=i)
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
                # 'hrly_data': update_hrly_data,  # Your existing hourly data
                # 'seasonal_data': seasonaldata,  # Your existing seasonal data
                # 'mobile_daily_data': mobile_daily_data  # Your existing mobile data
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
            
            # Get only today's data (24 hours = 96 data points max) (15 minutes data)
            now_time = timezone.now()
            today_start = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            raw_data = StationData.objects.filter(
                station=station, 
                timestamp__gte=today_start,
                timestamp__lte=now_time
            ).order_by('timestamp')
            
            # Debug: print all records and sum
            print("=== DEBUG: StationRawDataView ===")
            print(f"Station: {station.station_id}, Date: {today_start.date()} to {now_time}")
            print(f"Total records: {raw_data.count()}")
            total_rainfall = 0
            for record in raw_data:
                print(f"{record.timestamp} | {record.rainfall}")
                total_rainfall += record.rainfall
            print(f"Sum of rainfall: {total_rainfall}")
            print("=== END DEBUG ===")

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
