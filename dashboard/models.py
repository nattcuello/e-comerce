# dashboard/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class DashboardMetrics(models.Model):
    """
    Modelo para almacenar métricas del dashboard.
    Se actualiza periódicamente con estadísticas del negocio.
    """
    date = models.DateField(default=timezone.now)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Ventas totales del día
    total_orders = models.IntegerField(default=0)  # Número de pedidos del día
    new_users = models.IntegerField(default=0)  # Usuarios nuevos registrados
    page_views = models.IntegerField(default=0)  # Vistas de página
    conversion_rate = models.FloatField(default=0.0)  # Tasa de conversión (%)
    
    class Meta:
        verbose_name = "Dashboard Metric"
        verbose_name_plural = "Dashboard Metrics"
        unique_together = ['date']  # Una métrica por día
    
    def __str__(self):
        return f"Métricas del {self.date}"

class AdminNotification(models.Model):
    """
    Modelo para notificaciones del panel administrativo.
    Alertas sobre stock bajo, pedidos pendientes, etc.
    """
    NOTIFICATION_TYPES = [
        ('low_stock', 'Stock Bajo'),
        ('new_order', 'Nuevo Pedido'),
        ('payment_pending', 'Pago Pendiente'),
        ('system_alert', 'Alerta del Sistema'),
    ]
    
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)  # Título de la notificación
    message = models.TextField()  # Mensaje detallado
    is_read = models.BooleanField(default=False)  # Si fue leída o no
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']  # Más recientes primero
    
    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

class AdminAction(models.Model):
    """
    Modelo para registrar acciones administrativas.
    Bitácora de cambios realizados por los administradores.
    """
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50)  # Tipo de acción (create, update, delete)
    model_name = models.CharField(max_length=50)  # Modelo afectado
    object_id = models.CharField(max_length=50)  # ID del objeto modificado
    description = models.TextField()  # Descripción de la acción
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.action_type} {self.model_name}"