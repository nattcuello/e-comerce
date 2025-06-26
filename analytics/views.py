# analytics/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import SalesAnalytics, ProductAnalytics, WebsiteAnalytics, CustomerAnalytics
from orders.models import Order, OrderItem
from django.contrib.auth.models import User

def is_admin(user):
    """Verificar si el usuario es administrador"""
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def analytics_dashboard(request):
    """
    Dashboard principal de analytics con métricas generales.
    """
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    # Métricas de los últimos 30 días
    sales_data = SalesAnalytics.objects.filter(date__gte=last_30_days)
    
    total_revenue = sales_data.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0
    total_orders = sales_data.aggregate(Sum('total_orders'))['total_orders__sum'] or 0
    avg_order_value = sales_data.aggregate(Avg('average_order_value'))['average_order_value__avg'] or 0
    
    # Datos para gráficos
    daily_sales = list(sales_data.values('date', 'total_revenue', 'total_orders'))
    
    # Top 5 productos más vendidos
    top_products = ProductAnalytics.objects.filter(
        date__gte=last_30_days
    ).values('product_name').annotate(
        total_sold=Sum('units_sold'),
        total_revenue=Sum('revenue')
    ).order_by('-total_sold')[:5]
    
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'daily_sales': json.dumps(daily_sales, default=str),
        'top_products': top_products,
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def google_analytics_config(request):
    """
    Vista para configurar Google Analytics.
    Permite conectar con la API de Google Analytics.
    """
    if request.method == 'POST':
        # Aquí iría la lógica para configurar Google Analytics
        # Por ahora solo guardamos la configuración básica
        ga_tracking_id = request.POST.get('ga_tracking_id')
        ga_api_key = request.POST.get('ga_api_key')
        
        # Guardar en configuración (podrías usar django-constance o similar)
        # settings.GOOGLE_ANALYTICS_TRACKING_ID = ga_tracking_id
        
        return JsonResponse({'status': 'success', 'message': 'Configuración guardada'})
    
    return render(request, 'analytics/google_analytics_config.html')

# analytics/management/commands/update_analytics.py
# Este comando se ejecutará diariamente para actualizar las métricas
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import timedelta
from analytics.models import SalesAnalytics, ProductAnalytics, WebsiteAnalytics, CustomerAnalytics
from orders.models import Order, OrderItem
from django.contrib.auth.models import User

class Command(BaseCommand):
    """
    Comando para actualizar las métricas de analytics diariamente.
    Se puede ejecutar con: python manage.py update_analytics
    O programarlo con cron para que se ejecute automáticamente.
    """
    help = 'Actualiza las métricas de analytics para el día anterior'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Fecha específica para procesar (YYYY-MM-DD)',
        )
    
    def handle(self, *args, **options):
        # Determinar la fecha a procesar
        if options['date']:
            target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
        else:
            # Por defecto, procesar el día anterior
            target_date = timezone.now().date() - timedelta(days=1)
        
        self.stdout.write(f'Procesando métricas para: {target_date}')
        
        # Actualizar métricas de ventas
        self.update_sales_analytics(target_date)
        
        # Actualizar métricas de productos
        self.update_product_analytics(target_date)
        
        # Actualizar métricas de clientes
        self.update_customer_analytics(target_date)
        
        self.stdout.write(
            self.style.SUCCESS(f'Métricas actualizadas exitosamente para {target_date}')
        )
    
    def update_sales_analytics(self, date):
        """Actualizar métricas de ventas para una fecha específica"""
        # Obtener pedidos del día
        orders = Order.objects.filter(
            created_at__date=date,
            status__in=['confirmed', 'processing', 'shipped', 'delivered']  # Solo pedidos válidos
        )
        
        # Calcular métricas
        total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_orders = orders.count()
        total_items = OrderItem.objects.filter(order__in=orders).aggregate(Sum('quantity'))['quantity__sum'] or 0
        unique_customers = orders.values('user').distinct().count()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Métricas por horario
        morning_orders = orders.filter(created_at__hour__range=[6, 11])
        afternoon_orders = orders.filter(created_at__hour__range=[12, 17])
        evening_orders = orders.filter(created_at__hour__range=[18, 23])
        night_orders = orders.filter(created_at__hour__range=[0, 5])
        
        morning_sales = morning_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        afternoon_sales = afternoon_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        evening_sales = evening_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        night_sales = night_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Crear o actualizar registro
        sales_analytics, created = SalesAnalytics.objects.update_or_create(
            date=date,
            defaults={
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'total_items_sold': total_items,
                'average_order_value': avg_order_value,
                'unique_customers': unique_customers,
                'morning_sales': morning_sales,
                'afternoon_sales': afternoon_sales,
                'evening_sales': evening_sales,
                'night_sales': night_sales,
            }
        )
        
        action = "Creado" if created else "Actualizado"
        self.stdout.write(f'  - {action} SalesAnalytics: ${total_revenue} en {total_orders} pedidos')
    
    def update_product_analytics(self, date):
        """Actualizar métricas de productos para una fecha específica"""
        # Obtener items vendidos en la fecha
        order_items = OrderItem.objects.filter(
            order__created_at__date=date,
            order__status__in=['confirmed', 'processing', 'shipped', 'delivered']
        )
        
        # Agrupar por producto
        product_data = {}
        for item in order_items:
            product_id = item.product_id
            if product_id not in product_data:
                product_data[product_id] = {
                    'product_name': item.product_name,
                    'units_sold': 0,
                    'revenue': 0,
                }
            
            product_data[product_id]['units_sold'] += item.quantity
            product_data[product_id]['revenue'] += item.total_price
        
        # Crear registros de ProductAnalytics
        for product_id, data in product_data.items():
            ProductAnalytics.objects.update_or_create(
                date=date,
                product_id=product_id,
                defaults={
                    'product_name': data['product_name'],
                    'units_sold': data['units_sold'],
                    'revenue': data['revenue'],
                    'conversion_rate': 0.0,  # Se calculará cuando tengamos datos de vistas
                }
            )
        
        self.stdout.write(f'  - Procesados {len(product_data)} productos')
    
    def update_customer_analytics(self, date):
        """Actualizar métricas de clientes para una fecha específica"""
        # Nuevos clientes (usuarios registrados en la fecha)
        new_customers = User.objects.filter(date_joined__date=date).count()
        
        # Clientes que compraron en la fecha
        customers_who_bought = Order.objects.filter(
            created_at__date=date,
            status__in=['confirmed', 'processing', 'shipped', 'delivered']
        ).values('user').distinct().count()
        
        # Clientes que regresan (ya habían comprado antes)
        returning_customers = 0
        orders_today = Order.objects.filter(created_at__date=date)
        for order in orders_today:
            previous_orders = Order.objects.filter(
                user=order.user,
                created_at__date__lt=date
            ).exists()
            if previous_orders:
                returning_customers += 1
        
        CustomerAnalytics.objects.update_or_create(
            date=date,
            defaults={
                'new_customers': new_customers,
                'returning_customers': returning_customers,
                'total_active_customers': customers_who_bought,
            }
        )
        
        self.stdout.write(f'  - Clientes: {new_customers} nuevos, {returning_customers} recurrentes')