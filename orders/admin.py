from django.contrib import admin
from .models import (
    Product, State, PaymentMethod, PaymentStatus, Persona, Company,
    FiscalCondition, IvaCondition, CardInfo, Order, OrderDetail, OrderDetailCard
)


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0
    fields = ['product', 'quantity', 'unit_price', 'subtotal']
    readonly_fields = ['subtotal']


class OrderDetailCardInline(admin.TabularInline):
    model = OrderDetailCard
    extra = 0
    fields = [
        'product', 'card_info', 'quantity', 'unit_price', 'offer',
        'discount', 'cuotas', 'installments', 'subtotal', 'total_installments'
    ]
    readonly_fields = ['subtotal', 'total_installments']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'total', 'payment_status', 'is_active']
    list_filter = ['created_at', 'payment_status', 'is_active']
    search_fields = ['user__username', 'company__name', 'persona__name']
    inlines = [OrderDetailInline, OrderDetailCardInline]
    readonly_fields = ['created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(CardInfo)
class CardInfoAdmin(admin.ModelAdmin):
    list_display = ['card_holder', 'card_number', 'payment_method', 'expiration', 'is_active']
    search_fields = ['card_holder', 'card_number']
    list_filter = ['payment_method', 'is_active']


# Registro rápido para modelos simples
admin.site.register(State)
admin.site.register(PaymentMethod)
admin.site.register(PaymentStatus)
admin.site.register(Persona)
admin.site.register(Company)
admin.site.register(FiscalCondition)
admin.site.register(IvaCondition)
