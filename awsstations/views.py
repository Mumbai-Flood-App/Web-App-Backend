
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
    print('=== AWSSTATIONS StationDetailView IS RUNNING ===')
    def get(self, request, station_id):
        print("=== STATION DETAIL VIEW CODE IS LIVE ===")
        now_time = timezone.now()
        ist = pytz.timezone('Asia/Kolkata')
        
        # Use UTC dates for calculations
        today_utc = now_time.date()
        three_days_ago_utc = today_utc - timedelta(days=3)

        try:
            # Fetch station
            station = AWSStation.objects.get(station_id=station_id)
            serializer = AWSStationSerializer(station).data

            # Aggregate daily rainfall for the last 4 UTC days
            update_daily_data = []
            MAX_REASONABLE_RAINFALL = 1000  # mm, adjust as needed

            for i in range(4):
                day_utc = three_days_ago_utc + timedelta(days=i)
                # Use UTC midnight for start and end of day
                day_start = timezone.make_aware(datetime.combine(day_utc, datetime.min.time()))
                if day_utc == today_utc:
                    day_end = now_time
                else:
                    day_end = timezone.make_aware(datetime.combine(day_utc + timedelta(days=1), datetime.min.time()))
                
                print(f"UTC {day_utc} start: {day_start} ({day_start.tzinfo}), end: {day_end} ({day_end.tzinfo})")
                
                records = StationData.objects.filter(
                    station=station,
                    timestamp__gte=day_start,
                    timestamp__lt=day_end  # Use lt instead of lte to avoid double counting
                )
                
                for rec in records:
                    print(f"Included: {rec.timestamp} | {rec.rainfall}")
                print(f"Total records included for {day_utc}: {records.count()}")
                
                observed = sum(rec.rainfall for rec in records)
                print(f"UTC {day_utc} rainfall sum: {observed}")

                # Convert UTC date to IST for display
                day_ist = day_utc.astimezone(ist).date()
                
                # Get prediction for this day (using UTC date)
                pred_date = day_utc - timedelta(days=1)
                past_prediction = DaywisePrediction.objects.filter(
                    station=station,
                    timestamp__date=pred_date
                ).order_by('-timestamp').first()
                
                predicted_value = past_prediction.day1_rainfall if past_prediction else 0
                if predicted_value > MAX_REASONABLE_RAINFALL or predicted_value < 0:
                    predicted_value = 0

                update_daily_data.append({
                    'date': day_ist.strftime('%Y-%m-%d'),  # Display date in IST
                    'observed': observed,
                    'predicted': predicted_value,
                    'is_forecasted': False
                })

            # Get latest predictions for future days
            pred_daily_data = DaywisePrediction.objects.filter(
                station=station, 
                timestamp__isnull=False
            ).latest('timestamp')
            
            for i in range(1, 4):
                future_date_utc = today_utc + timedelta(days=i)
                future_date_ist = future_date_utc.astimezone(ist).date()
                update_daily_data.append({
                    'date': future_date_ist.strftime('%Y-%m-%d'),  # Display date in IST
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
            )class StationDetailView(APIView):
    print('=== AWSSTATIONS StationDetailView IS RUNNING ===')
    def get(self, request, station_id):
        print("=== STATION DETAIL VIEW CODE IS LIVE ===")
        now_time = timezone.now()
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = now_time.astimezone(ist)
        today_ist = now_ist.date()
        three_days_ago_ist = today_ist - timedelta(days=3)

        try:
            # Fetch station
            station = AWSStation.objects.get(station_id=station_id)
            serializer = AWSStationSerializer(station).data

            # Aggregate daily rainfall for the last 4 IST days
            update_daily_data = []
            MAX_REASONABLE_RAINFALL = 1000  # mm, adjust as needed

            for i in range(4):
                day = three_days_ago_ist + timedelta(days=i)
                day_start_naive = datetime.combine(day, datetime.min.time())
                day_start_ist = make_aware(day_start_naive, ist)
                if day == today_ist:
                    day_end = now_time
                else:
                    day_end_naive = datetime.combine(day, datetime.max.time())
                    day_end_ist = make_aware(day_end_naive, ist)
                    day_end = day_end_ist
                print(f"IST {day} start: {day_start_ist} ({day_start_ist.tzinfo}), end: {day_end} ({day_end.tzinfo})")
                records = StationData.objects.filter(
                    station=station,
                    timestamp__gte=day_start_ist,
                    timestamp__lte=day_end
                )
                for rec in records:
                    print(f"Included: {rec.timestamp} | {rec.rainfall}")
                print(f"Total records included for {day}: {records.count()}")
                observed = sum(rec.rainfall for rec in records)
                print(f"IST {day} rainfall sum: {observed}")

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
                    'date': day.strftime('%Y-%m-%d'),
                    'observed': observed,
                    'predicted': predicted_value,
                    'is_forecasted': False
                })

            # Get latest predictions for future days
            pred_daily_data = DaywisePrediction.objects.filter(
                station=station, 
                timestamp__isnull=False
            ).latest('timestamp')
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
