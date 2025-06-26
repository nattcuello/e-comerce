# orders/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Order(models.Model):
    """
    Modelo principal para los pedidos del ecommerce.
    Contiene toda la información del pedido y su estado.
    """
    ORDER_STATUS = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('processing', 'En Proceso'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('failed', 'Falló'),
        ('refunded', 'Reembolsado'),
    ]
    
    # Información básica del pedido
    order_number = models.CharField(max_length=20, unique=True)  # Número único del pedido
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Estado del pedido
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Información de envío
    shipping_address = models.TextField()  # Dirección completa de envío
    shipping_city = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_phone = models.CharField(max_length=20)
    
    # Información financiera
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # Subtotal sin envío
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total final
    
    # Información de pago
    payment_method = models.CharField(max_length=50, blank=True)  # MercadoPago, etc.
    payment_id = models.CharField(max_length=100, blank=True)  # ID del pago externo
    
    # Notas adicionales
    notes = models.TextField(blank=True)  # Notas del cliente o admin
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pedido {self.order_number} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Generar número de pedido automáticamente si no existe
        if not self.order_number:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.order_number = f"ORD-{timestamp}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    """
    Modelo para los items individuales de cada pedido.
    Cada producto en el pedido es un OrderItem.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # Nota: Estos campos se conectarán con la app products cuando esté lista
    product_id = models.IntegerField()  # ID del producto (temporal)
    product_name = models.CharField(max_length=200)  # Nombre del producto al momento del pedido
    product_sku = models.CharField(max_length=50, blank=True)  # SKU del producto
    quantity = models.PositiveIntegerField()  # Cantidad ordenada
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)  # Precio unitario al momento del pedido
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # quantity * unit_price
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity} - Pedido {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        # Calcular precio total automáticamente
        self.total_price = Decimal(str(self.quantity)) * self.unit_price
        super().save(*args, **kwargs)

class OrderTracking(models.Model):
    """
    Modelo para el seguimiento de pedidos.
    Registra cada cambio de estado del pedido.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=20)  # Estado al que cambió
    description = models.TextField()  # Descripción del cambio
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Admin que hizo el cambio
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pedido {self.order.order_number} - {self.status}"