from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import datetime, timedelta
import pandas as pd
from awsstations.models import AWSStation, StationData, DaywisePrediction
from weatherstations.models import WeatherStation, Waterlevel_Data
from crowdsource.models import CSFormData, Tweets

def is_staff(user):
    return user.is_staff

def login_view(request):
    """Handle staff login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'dashboard/login.html')

def logout_view(request):
    """Handle staff logout."""
    logout(request)
    return redirect('dashboard:login')

@login_required(login_url='dashboard:login')
@user_passes_test(is_staff, login_url='dashboard:login')
def dashboard(request):
    """Render the main dashboard page."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_sources = request.GET.getlist('sources[]', ['aws', 'prediction', 'tweet', 'crowd'])

    data = {}
    
    try:
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            # Default to last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

        if 'aws' in selected_sources:
            aws_data = StationData.objects.filter(
                timestamp__date__range=[start_date, end_date]
            ).select_related('station').order_by('-timestamp')[:100]
            data['aws_data'] = aws_data

        if 'prediction' in selected_sources:
            prediction_data = DaywisePrediction.objects.filter(
                timestamp__date__range=[start_date, end_date]
            ).select_related('station').order_by('-timestamp')[:100]
            data['prediction_data'] = prediction_data

        if 'tweet' in selected_sources:
            tweet_data = Tweets.objects.filter(
                timestamp__date__range=[start_date, end_date]
            ).order_by('-timestamp')[:100]
            data['tweet_data'] = tweet_data

        if 'crowd' in selected_sources:
            crowd_data = CSFormData.objects.filter(
                timestamp__date__range=[start_date, end_date]
            ).order_by('-timestamp')[:100]
            data['crowd_data'] = crowd_data

    except Exception as e:
        messages.error(request, f'Error fetching data: {str(e)}')

    return render(request, 'dashboard/index.html', {
        'user': request.user,
        'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
        'selected_sources': selected_sources,
        **data
    })

@login_required(login_url='dashboard:login')
@user_passes_test(is_staff, login_url='dashboard:login')
@csrf_exempt
def get_data(request, source):
    """Get data for a specific source within a date range."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        if source == 'aws':
            data = StationData.objects.filter(
                timestamp__date__range=[start_date, end_date]
            ).select_related('station').order_by('-timestamp')[:100]
            
            return JsonResponse({
                'data': [{
                    'station': item.station.name,
                    'rainfall': item.rainfall,
                    'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                } for item in data]
            })
            
        elif source == 'prediction':
            data = DaywisePrediction.objects.filter(
                timestamp__date__range=[start_date, end_date]
            ).select_related('station').order_by('-timestamp')[:100]
            
            return JsonResponse({
                'data': [{
                    'station': item.station.name,
                    'day1_rainfall': item.day1_rainfall,
                    'day2_rainfall': item.day2_rainfall,
                    'day3_rainfall': item.day3_rainfall,
                    'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                } for item in data]
            })
            
        elif source == 'tweet':
            data = Tweets.objects.filter(
                timestamp__date__range=[start_date, end_date]
            ).order_by('-timestamp')[:100]
            
            return JsonResponse({
                'data': [{
                    'text': item.tweet_text,
                    'sentiment': 'Positive' if item.sentiment else 'Negative',
                    'location': item.address,
                    'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                } for item in data]
            })
            
        elif source == 'crowd':
            data = CSFormData.objects.filter(
                timestamp__date__range=[start_date, end_date]
            ).order_by('-timestamp')[:100]
            
            return JsonResponse({
                'data': [{
                    'location': item.location,
                    'depth': f"{item.feet}ft {item.inch}in",
                    'feedback': item.feedback,
                    'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                } for item in data]
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid source'}, status=400)

@login_required(login_url='dashboard:login')
@user_passes_test(is_staff, login_url='dashboard:login')
@csrf_exempt
def download_data(request, source):
    """Download data for a specific source within a date range."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        filename = f"{source}_data_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        
        if source == 'aws':
            data = StationData.objects.filter(
                timestamp__date__range=[start_date, end_date]
            ).select_related('station').order_by('-timestamp')
            
            df = pd.DataFrame([{
                'station': item.station.name,
                'rainfall': item.rainfall,
                'timestamp': item.timestamp
            } for item in data])
            
        elif source == 'weather':
            data = Waterlevel_Data.objects.filter(
                timestamp__date__range=[start_date, end_date]
            ).select_related('station').order_by('-timestamp')
            
            df = pd.DataFrame([{
                'station': item.station.name,
                'water_level': item.waterlevel,
                'timestamp': item.timestamp
            } for item in data])
            
        elif source == 'crowd':
            data = CSFormData.objects.filter(
                timestamp__date__range=[start_date, end_date]
            ).order_by('-timestamp')
            
            df = pd.DataFrame([{
                'location': item.location,
                'depth_feet': item.feet,
                'depth_inches': item.inch,
                'feedback': item.feedback,
                'latitude': item.latitude,
                'longitude': item.longitude,
                'timestamp': item.timestamp
            } for item in data])
        else:
            return JsonResponse({'error': 'Invalid source'}, status=400)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        df.to_csv(response, index=False)
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
