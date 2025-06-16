# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('stations/', views.StationListView.as_view()),
    path('stations/<int:station_id>/', views.StationDetailView.as_view()),
    path('stations/<int:station_id>/rawdata/', views.StationRawDataView.as_view()),
    path('train/', views.TrainStationListView.as_view()),
    path('daily-station-data/<int:station_id>/', views.DailyStationDataListView.as_view()),
    path('quarterly-aws-data/<int:station_id>/', views.QuarterlyAWSDataListView.as_view())
]
