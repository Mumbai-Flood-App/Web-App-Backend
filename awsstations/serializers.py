from rest_framework import serializers
from .models import AWSStation, StationData, DaywisePrediction, HourlyPrediction, TrainStation, DailyStationData, HourlyAWSData

class AWSStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AWSStation
        fields = '__all__'

class StationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationData
        fields = 'rainfall', 'timestamp'

class TrainStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainStation
        fields = ['station_name', 'latitude', 'longitude', 'WarningLevel']

class DaywisePredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DaywisePrediction
        fields = [ 'day1_rainfall', 'day2_rainfall', 'day3_rainfall', 'timestamp']

class HourlyPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourlyPrediction
        fields = ['hr_24_rainfall']

class DailyStationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStationData
        fields = '__all__'

class HourlyAWSDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HourlyAWSData
        fields = '__all__'
