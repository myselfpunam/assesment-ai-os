from django.contrib import admin
from .models import Batch, StudentProfile, Enrollment


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'programme', 'year', 'is_active', 'created_at']
    list_filter = ['programme', 'year', 'is_active']
    search_fields = ['name']


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'programme', 'batch', 'enrollment_year', 'is_active']
    list_filter = ['programme', 'batch', 'is_active']
    search_fields = ['student_id', 'user__email', 'user__first_name']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'section', 'status', 'grade', 'created_at']
    list_filter = ['status']
    search_fields = ['student__student_id']
