from rest_framework import serializers
from .models import StudentAttempt, StudentAnswer


class StudentAnswerSerializer(serializers.ModelSerializer):
    question_text  = serializers.CharField(source='question.question_text', read_only=True)
    question_type  = serializers.CharField(source='question.question_type', read_only=True)
    max_marks      = serializers.IntegerField(source='question.marks', read_only=True)
    selected_options = serializers.SerializerMethodField()

    class Meta:
        model = StudentAnswer
        fields = [
            'id', 'question', 'question_text', 'question_type',
            'selected_options', 'text_answer',
            'is_correct', 'marks_obtained', 'max_marks',
            'graded_at',
        ]

    def get_selected_options(self, obj):
        return [
            {'id': str(opt.id), 'option_text': opt.option_text, 'is_correct': opt.is_correct}
            for opt in obj.selected_options.all()
        ]


class AttemptListSerializer(serializers.ModelSerializer):
    student_name   = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id_no  = serializers.CharField(source='student.student_id', read_only=True)
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)

    class Meta:
        model = StudentAttempt
        fields = [
            'id', 'student_name', 'student_id_no', 'assessment_title',
            'attempt_number', 'status', 'total_score', 'max_score',
            'percentage', 'is_passed', 'needs_manual_grading',
            'started_at', 'submitted_at',
        ]


class AttemptDetailSerializer(serializers.ModelSerializer):
    student_name    = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id_no   = serializers.CharField(source='student.student_id', read_only=True)
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)
    pass_marks      = serializers.IntegerField(source='assessment.pass_marks', read_only=True)
    answers         = StudentAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = StudentAttempt
        fields = [
            'id', 'student_name', 'student_id_no', 'assessment_title',
            'attempt_number', 'status', 'total_score', 'max_score',
            'percentage', 'is_passed', 'pass_marks', 'needs_manual_grading',
            'started_at', 'submitted_at', 'answers',
        ]


class SubmitAnswerItemSerializer(serializers.Serializer):
    question_id         = serializers.UUIDField()
    selected_option_ids = serializers.ListField(child=serializers.UUIDField(), required=False, default=list)
    text_answer         = serializers.CharField(required=False, allow_blank=True, default='')


class SubmitAttemptSerializer(serializers.Serializer):
    answers = SubmitAnswerItemSerializer(many=True)


class ManualGradeSerializer(serializers.Serializer):
    marks = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0)
