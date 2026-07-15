from django.contrib import admin
from .models import StudentAttempt, StudentAnswer


class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    fields = ['question', 'text_answer', 'is_correct', 'marks_obtained', 'graded_by']
    readonly_fields = ['question', 'graded_by', 'graded_at']


@admin.register(StudentAttempt)
class StudentAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment', 'attempt_number', 'status', 'total_score', 'max_score', 'percentage', 'is_passed', 'submitted_at']
    list_filter = ['status', 'is_passed', 'needs_manual_grading']
    search_fields = ['student__student_id', 'assessment__title']
    inlines = [StudentAnswerInline]


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct', 'marks_obtained', 'graded_by', 'graded_at']
    list_filter = ['is_correct']
