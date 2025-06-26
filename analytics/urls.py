# analytics/urls.py
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard de analytics
    path('', views.analytics_dashboard, name='dashboard'),
    
    # Configuración de Google Analytics
    path('google-analytics/', views.google_analytics_config, name='google_analytics_config'),
]

