from django.shortcuts import get_object_or_404
from .models import Assessment, Question, QuestionOption
from apps.courses.models import CourseSection


class AssessmentService:

    @staticmethod
    def create_assessment(section_id, user, data):
        section = get_object_or_404(CourseSection, id=section_id, deleted_at__isnull=True)
        assessment = Assessment.objects.create(
            section=section,
            created_by=user,
            title=data['title'],
            description=data.get('description', ''),
            assessment_type=data.get('assessment_type', 'quiz'),
            pass_marks=data.get('pass_marks', 0),
            duration_minutes=data.get('duration_minutes', 60),
            start_datetime=data.get('start_datetime'),
            end_datetime=data.get('end_datetime'),
            allow_multiple_attempts=data.get('allow_multiple_attempts', False),
            max_attempts=data.get('max_attempts', 1),
            shuffle_questions=data.get('shuffle_questions', False),
            show_result_immediately=data.get('show_result_immediately', True),
        )
        return assessment

    @staticmethod
    def get_assessments_for_section(section_id):
        return Assessment.objects.filter(
            section_id=section_id,
            deleted_at__isnull=True,
        ).select_related('section', 'created_by')

    @staticmethod
    def get_assessment(assessment_id):
        return get_object_or_404(
            Assessment,
            id=assessment_id,
            deleted_at__isnull=True,
        )

    @staticmethod
    def publish_assessment(assessment_id):
        assessment = get_object_or_404(
            Assessment, id=assessment_id, deleted_at__isnull=True
        )
        assessment.is_published = True
        assessment.save(update_fields=['is_published', 'updated_at'])
        return assessment

    @staticmethod
    def delete_assessment(assessment_id):
        from django.utils import timezone
        assessment = get_object_or_404(
            Assessment, id=assessment_id, deleted_at__isnull=True
        )
        assessment.deleted_at = timezone.now()
        assessment.save(update_fields=['deleted_at'])


class QuestionService:

    @staticmethod
    def add_question(assessment_id, data):
        assessment = get_object_or_404(
            Assessment, id=assessment_id, deleted_at__isnull=True
        )
        question = Question.objects.create(
            assessment=assessment,
            question_text=data['question_text'],
            question_type=data.get('question_type', 'mcq'),
            marks=data.get('marks', 1),
            order=data.get('order', 1),
            explanation=data.get('explanation', ''),
        )
        return question

    @staticmethod
    def delete_question(question_id):
        from django.utils import timezone
        question = get_object_or_404(
            Question, id=question_id, deleted_at__isnull=True
        )
        question.deleted_at = timezone.now()
        question.save(update_fields=['deleted_at'])


class QuestionOptionService:

    @staticmethod
    def add_option(question_id, data):
        question = get_object_or_404(
            Question, id=question_id, deleted_at__isnull=True
        )
        option = QuestionOption.objects.create(
            question=question,
            option_text=data['option_text'],
            is_correct=data.get('is_correct', False),
            order=data.get('order', 1),
        )
        return option

    @staticmethod
    def delete_option(option_id):
        from django.utils import timezone
        option = get_object_or_404(
            QuestionOption, id=option_id, deleted_at__isnull=True
        )
        option.deleted_at = timezone.now()
        option.save(update_fields=['deleted_at'])
