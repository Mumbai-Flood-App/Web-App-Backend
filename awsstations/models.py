from django.db import models
from django.utils import timezone

class AWSStation(models.Model):
    station_id = models.IntegerField()
    name = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    rainfall = models.FloatField(default=0)

    def __str__(self):
        return self.name
    

class StationData(models.Model):
    station = models.ForeignKey(AWSStation, on_delete=models.CASCADE)
    rainfall = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.station.name + " " + str(self.timestamp)
    

class DaywisePrediction(models.Model):
    station = models.ForeignKey(AWSStation, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now, null=True)
    day1_rainfall = models.FloatField(default=0)
    day2_rainfall = models.FloatField(default=0)
    day3_rainfall = models.FloatField(default=0)

    def __str__(self):
        return self.station.name + " " + str(self.timestamp)
   
    
class HourlyPrediction(models.Model):
    station = models.ForeignKey(AWSStation, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    hr_24_rainfall = models.JSONField(default=dict)

    def __str__(self):
        return self.station.name + " " + str(self.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
    

class TrainStation(models.Model):
    station_code = models.IntegerField(primary_key=True)
    station_name = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    neareststation = models.ForeignKey( 'AWSStation' , on_delete=models.CASCADE, blank=True, null=True)
    WarningLevel = models.IntegerField(default=0)

    def __str__(self):
        return self.station_name

class DailyStationData(models.Model):
    station = models.ForeignKey('AWSStation', on_delete=models.CASCADE)
    date = models.DateField()
    total_rainfall = models.FloatField()

    def __str__(self):
        return f"{self.station.name} - {self.date} - {self.total_rainfall}"

class HourlyAWSData(models.Model):
    station = models.ForeignKey('AWSStation', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()  # Stores both date and time (15-min interval)
    rainfall = models.FloatField()

    def __str__(self):
        return f"{self.station.name} - {self.timestamp} - {self.rainfall}"
    
