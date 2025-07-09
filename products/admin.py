from django.contrib import admin
from .models import Product, Audit

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'stock', 'active')
    search_fields = ('name', 'description')
    list_filter = ('category', 'brand', 'active')

@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_id', 'affected_table', 'date')
    list_filter = ('action_id', 'affected_table', 'user')
    search_fields = ('description',)
    ordering = ('-date',)
