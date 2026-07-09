from rest_framework import serializers
from .models import Assessment, Question, QuestionOption


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'option_text', 'is_correct', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'assessment', 'question_text', 'question_type',
            'marks', 'order', 'explanation', 'is_active', 'options',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'assessment', 'created_at', 'updated_at']


class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'question_text', 'question_type', 'marks', 'order', 'explanation',
        ]


class QuestionOptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['option_text', 'is_correct', 'order']


class AssessmentListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    section_code = serializers.CharField(source='section.section_code', read_only=True)

    class Meta:
        model = Assessment
        fields = [
            'id', 'title', 'assessment_type', 'total_marks', 'pass_marks',
            'duration_minutes', 'start_datetime', 'end_datetime',
            'is_published', 'is_active', 'question_count', 'section_code',
            'created_at',
        ]

    def get_question_count(self, obj):
        return obj.questions.filter(is_active=True, deleted_at__isnull=True).count()


class AssessmentDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = [
            'id', 'section', 'created_by', 'title', 'description',
            'assessment_type', 'total_marks', 'pass_marks', 'duration_minutes',
            'start_datetime', 'end_datetime', 'allow_multiple_attempts',
            'max_attempts', 'shuffle_questions', 'show_result_immediately',
            'is_published', 'is_active', 'question_count', 'questions',
            'created_at', 'updated_at',
        ]

    def get_question_count(self, obj):
        return obj.questions.filter(is_active=True, deleted_at__isnull=True).count()


class AssessmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = [
            'title', 'description', 'assessment_type', 'pass_marks',
            'duration_minutes', 'start_datetime', 'end_datetime',
            'allow_multiple_attempts', 'max_attempts',
            'shuffle_questions', 'show_result_immediately',
        ]
