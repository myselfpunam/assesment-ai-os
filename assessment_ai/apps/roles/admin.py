from django.contrib import admin
from .models import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'display_name']
