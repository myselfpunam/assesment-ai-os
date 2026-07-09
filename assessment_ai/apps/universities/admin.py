from django.contrib import admin
from .models import University, UniversitySettings
from .models import UniversityAdmin as UniversityAdminModel


class UniversitySettingsInline(admin.StackedInline):
    model = UniversitySettings
    can_delete = False
    extra = 0


class UniversityAdminInline(admin.TabularInline):
    model = UniversityAdminModel
    extra = 0
    fields = ['user', 'is_primary', 'assigned_by', 'created_at']
    readonly_fields = ['created_at']


@admin.register(University)
class UniversityModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'city', 'country', 'is_active', 'created_at']
    list_filter = ['is_active', 'country']
    search_fields = ['name', 'slug', 'email']
    inlines = [UniversitySettingsInline, UniversityAdminInline]
    readonly_fields = ['slug', 'created_at', 'updated_at', 'created_by']


@admin.register(UniversitySettings)
class UniversitySettingsAdmin(admin.ModelAdmin):
    list_display = ['university', 'max_students', 'allow_ai_generation', 'updated_at']
    search_fields = ['university__name']


@admin.register(UniversityAdminModel)
class UniversityAdminAdmin(admin.ModelAdmin):
    list_display = ['user', 'university', 'is_primary', 'created_at']
    list_filter = ['is_primary']
