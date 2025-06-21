from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'role_id', 'is_active', 'created_at']
    search_fields = ['name', 'email']
    list_filter = ['role_id', 'is_active']
