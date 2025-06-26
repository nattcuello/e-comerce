# analytics/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SalesAnalytics(models.Model):
    """
    Modelo para análisis de ventas diarias.
    Se actualiza automáticamente cada día con las métricas de ventas.
    """
    date = models.DateField(unique=True)  # Una entrada por día
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Ingresos totales
    total_orders = models.IntegerField(default=0)  # Total de pedidos
    total_items_sold = models.IntegerField(default=0)  # Total de productos vendidos
    average_order_value = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # Valor promedio por pedido
    unique_customers = models.IntegerField(default=0)  # Clientes únicos que compraron
    
    # Análisis por horarios (para saber cuándo se vende más)
    morning_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 6-12 hrs
    afternoon_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 12-18 hrs
    evening_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 18-24 hrs
    night_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 0-6 hrs
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Sales Analytics"
        verbose_name_plural = "Sales Analytics"
    
    def __str__(self):
        return f"Ventas del {self.date}"

class ProductAnalytics(models.Model):
    """
    Modelo para análisis de productos.
    Registra cuáles productos se venden más, tendencias, etc.
    """
    date = models.DateField()
    product_id = models.IntegerField()  # ID del producto (se conectará con products app)
    product_name = models.CharField(max_length=200)  # Nombre del producto
    product_category = models.CharField(max_length=100, blank=True)  # Categoría del producto
    
    # Métricas del producto
    units_sold = models.IntegerField(default=0)  # Unidades vendidas
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Ingresos del producto
    views = models.IntegerField(default=0)  # Veces que fue visto (si tenemos tracking)
    conversion_rate = models.FloatField(default=0.0)  # Tasa de conversión vista -> compra
    
    class Meta:
        unique_together = ['date', 'product_id']  # Una entrada por producto por día
        ordering = ['-date', '-units_sold']
    
    def __str__(self):
        return f"{self.product_name} - {self.date}"

class WebsiteAnalytics(models.Model):
    """
    Modelo para métricas del sitio web.
    Conecta con Google Analytics para obtener datos de tráfico.
    """
    date = models.DateField(unique=True)
    
    # Métricas de tráfico
    page_views = models.IntegerField(default=0)  # Páginas vistas
    unique_visitors = models.IntegerField(default=0)  # Visitantes únicos
    sessions = models.IntegerField(default=0)  # Sesiones totales
    bounce_rate = models.FloatField(default=0.0)  # Tasa de rebote
    avg_session_duration = models.FloatField(default=0.0)  # Duración promedio de sesión (segundos)
    
    # Métricas de conversión
    visitors_to_customers = models.IntegerField(default=0)  # Visitantes que se convirtieron en clientes
    conversion_rate = models.FloatField(default=0.0)  # Tasa de conversión general
    
    # Fuentes de tráfico
    organic_traffic = models.IntegerField(default=0)  # Tráfico orgánico
    direct_traffic = models.IntegerField(default=0)  # Tráfico directo
    social_traffic = models.IntegerField(default=0)  # Tráfico de redes sociales
    referral_traffic = models.IntegerField(default=0)  # Tráfico de referidos
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Website Analytics"
        verbose_name_plural = "Website Analytics"
    
    def __str__(self):
        return f"Analytics del {self.date}"

class CustomerAnalytics(models.Model):
    """
    Modelo para análisis de comportamiento de clientes.
    Segmentación y métricas de clientes.
    """
    date = models.DateField()
    
    # Métricas de clientes
    new_customers = models.IntegerField(default=0)  # Clientes nuevos del día
    returning_customers = models.IntegerField(default=0)  # Clientes que regresan
    total_active_customers = models.IntegerField(default=0)  # Clientes activos en el período
    
    # Análisis de valor del cliente
    avg_customer_lifetime_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_order_frequency = models.FloatField(default=0.0)  # Frecuencia promedio de pedidos
    
    class Meta:
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Customer Analytics del {self.date}"