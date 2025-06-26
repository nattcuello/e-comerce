# dashboard/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

from orders.models import Order, OrderItem, OrderTracking
from analytics.models import SalesAnalytics, ProductAnalytics, WebsiteAnalytics
from .models import DashboardMetrics, AdminNotification, AdminAction
from django.contrib.auth.models import User

def is_admin(user):
    """Verificar si el usuario es administrador"""
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def dashboard_home(request):
    """
    Vista principal del dashboard administrativo.
    Muestra métricas generales y resumen del negocio.
    """
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    last_30_days = today - timedelta(days=30)
    
    # Métricas del día actual
    today_orders = Order.objects.filter(created_at__date=today)
    today_revenue = today_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    today_orders_count = today_orders.count()
    
    # Métricas de ayer para comparación
    yesterday_orders = Order.objects.filter(created_at__date=yesterday)
    yesterday_revenue = yesterday_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    yesterday_orders_count = yesterday_orders.count()
    
    # Calcular porcentajes de cambio
    revenue_change = calculate_percentage_change(yesterday_revenue, today_revenue)
    orders_change = calculate_percentage_change(yesterday_orders_count, today_orders_count)
    
    # Métricas de los últimos 30 días
    monthly_orders = Order.objects.filter(created_at__date__gte=last_30_days)
    monthly_revenue = monthly_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_customers = monthly_orders.values('user').distinct().count()
    avg_order_value = monthly_orders.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
    
    # Pedidos pendientes que necesitan atención
    pending_orders = Order.objects.filter(
        status__in=['pending', 'confirmed']
    ).order_by('-created_at')[:5]
    
    # Últimas notificaciones
    recent_notifications = AdminNotification.objects.filter(
        is_read=False
    ).order_by('-created_at')[:5]
    
    # Datos para gráfico de ventas (últimos 7 días)
    sales_chart_data = []
    for i in range(7):
        date = today - timedelta(days=i)
        day_orders = Order.objects.filter(created_at__date=date)
        day_revenue = day_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        sales_chart_data.append({
            'date': date.strftime('%d/%m'),
            'revenue': float(day_revenue),
            'orders': day_orders.count()
        })
    sales_chart_data.reverse()  # Mostrar del más antiguo al más reciente
    
    # Top 5 productos más vendidos este mes
    top_products = []
    try:
        top_products = ProductAnalytics.objects.filter(
            date__gte=last_30_days
        ).values('product_name').annotate(
            total_sold=Sum('units_sold'),
            total_revenue=Sum('revenue')
        ).order_by('-total_sold')[:5]
    except:
        # Si no hay datos de ProductAnalytics, calcular desde OrderItem
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT product_name, SUM(quantity) as total_sold, SUM(total_price) as total_revenue
                FROM orders_orderitem oi
                JOIN orders_order o ON oi.order_id = o.id
                WHERE o.created_at >= %s AND o.status IN ('confirmed', 'processing', 'shipped', 'delivered')
                GROUP BY product_name
                ORDER BY total_sold DESC
                LIMIT 5
            """, [last_30_days])
            top_products = [
                {
                    'product_name': row[0],
                    'total_sold': row[1],
                    'total_revenue': row[2]
                }
                for row in cursor.fetchall()
            ]
    
    context = {
        # Métricas del día
        'today_revenue': today_revenue,
        'today_orders': today_orders_count,
        'revenue_change': revenue_change,
        'orders_change': orders_change,
        
        # Métricas mensuales
        'monthly_revenue': monthly_revenue,
        'monthly_customers': monthly_customers,
        'avg_order_value': avg_order_value,
        
        # Datos para componentes
        'pending_orders': pending_orders,
        'recent_notifications': recent_notifications,
        'sales_chart_data': json.dumps(sales_chart_data),
        'top_products': top_products,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
@user_passes_test(is_admin)
def sales_report(request):
    """
    Vista para reportes detallados de ventas.
    Permite filtrar por fechas y exportar datos.
    """
    # Obtener parámetros de filtrado
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status_filter = request.GET.get('status', 'all')
    
    # Configurar fechas por defecto (último mes)
    if not date_from:
        date_from = (timezone.now().date() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = timezone.now().date().strftime('%Y-%m-%d')
    
    # Construir query base
    orders_query = Order.objects.all()
    
    # Aplicar filtros
    if date_from:
        orders_query = orders_query.filter(created_at__date__gte=date_from)
    if date_to:
        orders_query = orders_query.filter(created_at__date__lte=date_to)
    if status_filter != 'all':
        orders_query = orders_query.filter(status=status_filter)
    
    orders = orders_query.order_by('-created_at')
    
    # Calcular métricas del período
    total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders.count()
    avg_order_value = orders.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
    total_items = OrderItem.objects.filter(order__in=orders).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Paginación
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para gráfico de ventas diarias
    daily_sales = []
    current_date = datetime.strptime(date_from, '%Y-%m-%d').date()
    end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    while current_date <= end_date:
        day_orders = orders.filter(created_at__date=current_date)
        day_revenue = day_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        daily_sales.append({
            'date': current_date.strftime('%d/%m'),
            'revenue': float(day_revenue),
            'orders': day_orders.count()
        })
        current_date += timedelta(days=1)
    
    context = {
        'orders': page_obj,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'total_items': total_items,
        'date_from': date_from,
        'date_to': date_to,
        'status_filter': status_filter,
        'daily_sales': json.dumps(daily_sales),
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'dashboard/sales_report.html', context)

@login_required
@user_passes_test(is_admin)
def orders_management(request):
    """
    Vista para gestión de pedidos.
    Permite ver, filtrar y actualizar pedidos.
    """
    # Filtros
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    date_filter = request.GET.get('date', 'all')
    
    # Query base
    orders = Order.objects.all()
    
    # Aplicar filtros
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(shipping_phone__icontains=search_query)
        )
    
    if date_filter == 'today':
        orders = orders.filter(created_at__date=timezone.now().date())
    elif date_filter == 'week':
        week_ago = timezone.now().date() - timedelta(days=7)
        orders = orders.filter(created_at__date__gte=week_ago)
    elif date_filter == 'month':
        month_ago = timezone.now().date() - timedelta(days=30)
        orders = orders.filter(created_at__date__gte=month_ago)
    
    orders = orders.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas rápidas
    stats = {
        'total': Order.objects.count(),
        'pending': Order.objects.filter(status='pending').count(),
        'confirmed': Order.objects.filter(status='confirmed').count(),
        'shipped': Order.objects.filter(status='shipped').count(),
        'delivered': Order.objects.filter(status='delivered').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
    }
    
    context = {
        'orders': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'date_filter': date_filter,
        'status_choices': Order.STATUS_CHOICES,
        'stats': stats,
    }
    
    return render(request, 'dashboard/orders_management.html', context)

@login_required
@user_passes_test(is_admin)
def order_detail(request, order_id):
    """
    Vista detallada de un pedido específico.
    Permite ver toda la información y actualizar el estado.
    """
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            description = request.POST.get('description', '')
            
            if new_status in dict(Order.STATUS_CHOICES):
                # Actualizar estado del pedido
                old_status = order.status
                order.status = new_status
                order.save()
                
                # Crear registro de tracking
                OrderTracking.objects.create(
                    order=order,
                    status=new_status,
                    description=description or f'Estado actualizado de {old_status} a {new_status}',
                    created_by=request.user
                )
                
                # Registrar acción administrativa
                AdminAction.objects.create(
                    admin_user=request.user,
                    action_type='update',
                    model_name='Order',
                    object_id=str(order.id),
                    description=f'Estado actualizado de {old_status} a {new_status}'
                )
                
                messages.success(request, f'Estado del pedido actualizado a {order.get_status_display()}')
            else:
                messages.error(request, 'Estado inválido')
        
        elif action == 'add_note':
            note = request.POST.get('note')
            if note:
                order.notes = f"{order.notes}\n\n[{timezone.now().strftime('%d/%m/%Y %H:%M')}] {request.user.username}: {note}" if order.notes else f"[{timezone.now().strftime('%d/%m/%Y %H:%M')}] {request.user.username}: {note}"
                order.save()
                messages.success(request, 'Nota agregada correctamente')
        
        return redirect('dashboard:order_detail', order_id=order.id)
    
    # Obtener tracking del pedido
    tracking_history = order.tracking.all().order_by('-created_at')
    
    context = {
        'order': order,
        'tracking_history': tracking_history,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'dashboard/order_detail.html', context)

@login_required
@user_passes_test(is_admin)
def notifications_view(request):
    """
    Vista para gestionar notificaciones administrativas.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'mark_read':
            notification_id = request.POST.get('notification_id')
            try:
                notification = AdminNotification.objects.get(id=notification_id)
                notification.is_read = True
                notification.save()
                return JsonResponse({'status': 'success'})
            except AdminNotification.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Notificación no encontrada'})
        
        elif action == 'mark_all_read':
            AdminNotification.objects.filter(is_read=False).update(is_read=True)
            return JsonResponse({'status': 'success'})
    
    # Obtener notificaciones
    notifications = AdminNotification.objects.all().order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    # Paginación
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': unread_count,
    }
    
    return render(request, 'dashboard/notifications.html', context)

@login_required
@user_passes_test(is_admin)
def analytics_api(request):
    """
    API endpoint para obtener datos de gráficos via AJAX.
    """
    chart_type = request.GET.get('type', 'sales')
    days = int(request.GET.get('days', 30))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    if chart_type == 'sales':
        # Datos de ventas por día
        data = []
        current_date = start_date
        
        while current_date <= end_date:
            day_orders = Order.objects.filter(created_at__date=current_date)
            revenue = day_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            orders_count = day_orders.count()
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'revenue': float(revenue),
                'orders': orders_count
            })
            current_date += timedelta(days=1)
        
        return JsonResponse({
            'labels': [item['date'] for item in data],
            'revenue': [item['revenue'] for item in data],
            'orders': [item['orders'] for item in data]
        })
    
    elif chart_type == 'products':
        # Top productos vendidos
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT product_name, SUM(quantity) as total_sold
                FROM orders_orderitem oi
                JOIN orders_order o ON oi.order_id = o.id
                WHERE o.created_at >= %s AND o.status IN ('confirmed', 'processing', 'shipped', 'delivered')
                GROUP BY product_name
                ORDER BY total_sold DESC
                LIMIT 10
            """, [start_date])
            
            results = cursor.fetchall()
            
        return JsonResponse({
            'labels': [row[0] for row in results],
            'data': [row[1] for row in results]
        })
    
    elif chart_type == 'status':
        # Distribución de estados de pedidos
        status_data = []
        for status_code, status_name in Order.STATUS_CHOICES:
            count = Order.objects.filter(
                status=status_code,
                created_at__date__gte=start_date
            ).count()
            if count > 0:
                status_data.append({
                    'label': status_name,
                    'value': count
                })
        
        return JsonResponse({
            'labels': [item['label'] for item in status_data],
            'data': [item['value'] for item in status_data]
        })
    
    return JsonResponse({'error': 'Tipo de gráfico no válido'})

def calculate_percentage_change(old_value, new_value):
    """
    Calcular el porcentaje de cambio entre dos valores.
    """
    if old_value == 0:
        return 100 if new_value > 0 else 0
    
    change = ((new_value - old_value) / old_value) * 100
    return round(change, 1)