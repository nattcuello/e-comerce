from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Configuración del admin para los pedidos.
    Permite gestionar pedidos desde el panel de Django Admin.
    """
    list_display = [
        'order_number', 
        'user', 
        'status_badge', 
        'payment_status_badge',
        'total_amount', 
        'created_at',
        'view_details_link'
    ]
    
    list_filter = [
        'status', 
        'payment_status', 
        'created_at',
        'shipping_city'
    ]
    
    search_fields = [
        'order_number', 
        'user__username', 
        'user__email',
        'shipping_phone'
    ]
    
    readonly_fields = [
        'order_number', 
        'created_at', 
        'updated_at',
        'subtotal',
        'total_amount'
    ]
    
    # Campos organizados en fieldsets para mejor visualización
    fieldsets = (
        ('Información General', {
            'fields': ('order_number', 'user', 'created_at', 'updated_at')
        }),
        ('Estado', {
            'fields': ('status', 'payment_status')
        }),
        ('Información de Envío', {
            'fields': (
                'shipping_address', 
                'shipping_city', 
                'shipping_postal_code', 
                'shipping_phone'
            )
        }),
        ('Información Financiera', {
            'fields': (
                'subtotal', 
                'shipping_cost', 
                'tax_amount', 
                'total_amount'
            )
        }),
        ('Pago', {
            'fields': ('payment_method', 'payment_id')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
    )
    
    # Filtros por fecha en la barra lateral
    date_hierarchy = 'created_at'
    
    # Acciones personalizadas
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']
    
    def status_badge(self, obj):
        """
        Muestra el estado del pedido como un badge colorido.
        """
        colors = {
            'pending': '#ffc107',      # Amarillo
            'confirmed': '#17a2b8',    # Azul
            'processing': '#6f42c1',   # Púrpura
            'shipped': '#fd7e14',      # Naranja
            'delivered': '#28a745',    # Verde
            'cancelled': '#dc3545',    # Rojo
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 5px; border-radius: 5px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'

    def payment_status_badge(self, obj):
        """
        Muestra el estado del pago como un badge colorido.
        """
        colors = {
            'paid': '#28a745',     # Verde
            'pending': '#ffc107',  # Amarillo
            'failed': '#dc3545',   # Rojo
        }
        color = colors.get(obj.payment_status, '#6c757d')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 5px; border-radius: 5px;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Pago'

    def view_details_link(self, obj):
        """
        Genera un enlace para ver y editar los detalles del pedido.
        """
        url = reverse('admin:orders_order_change', args=[obj.id])
        return format_html('<a href="{}">Ver detalles</a>', url)
    view_details_link.short_description = 'Detalles'
