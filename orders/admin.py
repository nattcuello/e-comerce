from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Product, PaymentMethod, PaymentStatus, Persona, Company,
    FiscalCondition, CardInfo, Order, OrderDetail, OrderDetailCard
)

# -------- INLINES -------- #

class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0
    fields = ['product', 'quantity', 'unit_price', 'subtotal']
    readonly_fields = ['subtotal']
    show_change_link = True


class OrderDetailCardInline(admin.TabularInline):
    model = OrderDetailCard
    extra = 0
    fields = [
        'product', 'card_info', 'quantity', 'unit_price', 'offer',
        'discount', 'cuotas', 'installments', 'unit_price_with_offer',
        'subtotal', 'total_installments'
    ]
    readonly_fields = ['unit_price_with_offer', 'subtotal', 'total_installments']
    show_change_link = True

# -------- ORDER ADMIN -------- #

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status_badge', 'payment_status_badge',
        'total', 'created_at', 'view_details_link'
    ]
    
    list_filter = ['status', 'payment_status', 'created_at', 'shipping_city']
    search_fields = ['order_number', 'user__username', 'user__email', 'shipping_phone']
    readonly_fields = ['order_number', 'created_at', 'total']
    date_hierarchy = 'created_at'
    inlines = [OrderDetailInline, OrderDetailCardInline]
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']

    fieldsets = (
        ('Información General', {
            'fields': ('order_number', 'user', 'created_at')
        }),
        ('Estado de Orden', {
            'fields': ('status', 'payment_status')
        }),
        ('Envío', {
            'fields': (
                'shipping_address', 'shipping_city', 
                'shipping_postal_code', 'shipping_phone'
            )
        }),
        ('Totales', {
            'fields': ('shipping_cost', 'tax_amount', 'total')
        }),
        ('Facturación', {
            'fields': ('fiscal_condition', 'company', 'persona')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107', 'confirmed': '#17a2b8',
            'processing': '#6f42c1', 'shipped': '#fd7e14',
            'delivered': '#28a745', 'cancelled': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="color:white;background:{};padding:4px;border-radius:4px;">{}</span>',
                           color, obj.get_status_display())
    status_badge.short_description = 'Estado'

    def payment_status_badge(self, obj):
        colors = {
            'paid': '#28a745', 'pending': '#ffc107', 'failed': '#dc3545'
        }
        color = colors.get(obj.payment_status, '#6c757d')
        return format_html('<span style="color:white;background:{};padding:4px;border-radius:4px;">{}</span>',
                           color, obj.get_payment_status_display())
    payment_status_badge.short_description = 'Pago'

    def view_details_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.id])
        return format_html('<a href="{}">Ver detalles</a>', url)
    view_details_link.short_description = 'Detalles'

    # -------- ACCIONES PERSONALIZADAS -------- #
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"{updated} orden(es) marcadas como confirmadas.")
    mark_as_confirmed.short_description = "Marcar como Confirmadas"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f"{updated} orden(es) marcadas como enviadas.")
    mark_as_shipped.short_description = "Marcar como Enviadas"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f"{updated} orden(es) marcadas como entregadas.")
    mark_as_delivered.short_description = "Marcar como Entregadas"


# -------- DEMÁS MODELOS -------- #

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(CardInfo)
class CardInfoAdmin(admin.ModelAdmin):
    list_display = ['card_holder', 'payment_method', 'card_number', 'expiration', 'is_active']
    search_fields = ['card_holder', 'card_number']
    list_filter = ['payment_method', 'is_active']


# Registro directo para tablas de referencia
simple_models = [PaymentMethod, PaymentStatus, Persona, Company, FiscalCondition]
for model in simple_models:
    admin.site.register(model)
