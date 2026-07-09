from django.contrib import admin
from .models import Department, Programme, AcademicLevel, Semester


class ProgrammeInline(admin.TabularInline):
    model = Programme
    extra = 0
    fields = ['name', 'code', 'degree_type', 'is_active']


class AcademicLevelInline(admin.TabularInline):
    model = AcademicLevel
    extra = 0
    fields = ['name', 'level_number', 'is_active']


class SemesterInline(admin.TabularInline):
    model = Semester
    extra = 0
    fields = ['name', 'semester_number', 'start_date', 'end_date', 'is_current']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'university', 'is_active', 'created_at']
    list_filter = ['university', 'is_active']
    search_fields = ['name', 'code']
    inlines = [ProgrammeInline]


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'degree_type', 'department', 'is_active']
    list_filter = ['degree_type', 'is_active']
    search_fields = ['name', 'code']
    inlines = [AcademicLevelInline]


@admin.register(AcademicLevel)
class AcademicLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'level_number', 'programme', 'is_active']
    inlines = [SemesterInline]


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name', 'semester_number', 'academic_level', 'is_current', 'start_date', 'end_date']
    list_filter = ['is_current', 'is_active']
