from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('data/<str:source>/', views.get_data, name='get_data'),
    path('download/<str:source>/', views.download_data, name='download_data'),
]
