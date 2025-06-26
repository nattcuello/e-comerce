from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # URL principal del dashboard
    path('', views.dashboard_home, name='home'),
    
    # Reportes de ventas
    path('sales/', views.sales_report, name='sales_report'),
    
    # Gestión de pedidos
    path('orders/', views.orders_management, name='orders_management'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Notificaciones
    path('notifications/', views.notifications_view, name='notifications'),
    
    # API para gráficos (AJAX)
    path('api/analytics/', views.analytics_api, name='analytics_api'),
]