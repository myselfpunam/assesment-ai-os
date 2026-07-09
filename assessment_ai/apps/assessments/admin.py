from django.contrib import admin
from .models import Assessment, Question, QuestionOption


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 2
    fields = ['option_text', 'is_correct', 'order']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['question_text', 'question_type', 'marks', 'order']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'assessment_type', 'section', 'total_marks', 'is_published', 'is_active', 'created_at']
    list_filter = ['assessment_type', 'is_published', 'is_active']
    search_fields = ['title', 'section__section_code']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'question_type', 'marks', 'order', 'assessment', 'is_active']
    list_filter = ['question_type', 'is_active']
    search_fields = ['question_text']
    inlines = [QuestionOptionInline]


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ['option_text', 'is_correct', 'order', 'question']
    list_filter = ['is_correct']
