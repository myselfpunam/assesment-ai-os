from django.contrib import admin
from .models import Course, CourseSection, LecturerAssignment


class CourseSectionInline(admin.TabularInline):
    model = CourseSection
    extra = 0
    fields = ['section_code', 'semester', 'max_students', 'is_active']


class LecturerAssignmentInline(admin.TabularInline):
    model = LecturerAssignment
    extra = 0
    fields = ['lecturer', 'is_primary']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'credit_hours', 'is_active', 'created_at']
    list_filter = ['department', 'is_active', 'credit_hours']
    search_fields = ['name', 'code']
    inlines = [CourseSectionInline]


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ['section_code', 'course', 'semester', 'max_students', 'is_active']
    list_filter = ['course__department', 'is_active']
    search_fields = ['section_code', 'course__name']
    inlines = [LecturerAssignmentInline]


@admin.register(LecturerAssignment)
class LecturerAssignmentAdmin(admin.ModelAdmin):
    list_display = ['lecturer', 'section', 'is_primary', 'assigned_by']
    list_filter = ['is_primary']
