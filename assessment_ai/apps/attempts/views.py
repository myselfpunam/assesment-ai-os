from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from core.utils.response import ApiResponse
from .services import AttemptService
from .serializers import (
    AttemptListSerializer,
    AttemptDetailSerializer,
    SubmitAttemptSerializer,
    ManualGradeSerializer,
)


class StartAttemptView(APIView):
    """Student starts an attempt on a published assessment."""
    permission_classes = [IsAuthenticated]

    def post(self, request, assessment_id):
        student_profile_id = request.data.get('student_profile_id')
        if not student_profile_id:
            return ApiResponse.error('student_profile_id is required.')
        try:
            attempt = AttemptService.start_attempt(assessment_id, student_profile_id)
        except ValueError as e:
            return ApiResponse.error(str(e))
        return ApiResponse.created(
            AttemptDetailSerializer(attempt).data,
            'Attempt started. Good luck!',
        )


class SubmitAttemptView(APIView):
    """Student submits answers — MCQ/T-F auto-graded instantly."""
    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):
        serializer = SubmitAttemptSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.error('Validation failed.', serializer.errors)
        try:
            attempt = AttemptService.submit_attempt(
                attempt_id=attempt_id,
                answers_data=serializer.validated_data['answers'],
            )
        except ValueError as e:
            return ApiResponse.error(str(e))

        result_msg = (
            f"Submitted! Score: {attempt.total_score}/{attempt.max_score} "
            f"({attempt.percentage:.1f}%) — {'PASSED ✓' if attempt.is_passed else 'FAILED ✗'}"
        )
        if attempt.needs_manual_grading:
            result_msg += " · Some answers need manual grading by lecturer."

        return ApiResponse.success(
            AttemptDetailSerializer(attempt).data,
            result_msg,
        )


class AttemptDetailView(APIView):
    """Get a single attempt with all answers and scores."""
    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):
        attempt = AttemptService.get_attempt(attempt_id)
        return ApiResponse.success(
            AttemptDetailSerializer(attempt).data,
            'Attempt retrieved.',
        )


class AssessmentAttemptsView(APIView):
    """Lecturer views all student attempts for an assessment."""
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id):
        attempts = AttemptService.get_attempts_for_assessment(assessment_id)
        serializer = AttemptListSerializer(attempts, many=True)
        return ApiResponse.success(
            serializer.data,
            f'{attempts.count()} attempts found.',
        )


class StudentAttemptsView(APIView):
    """Get all attempts by a student across all assessments."""
    permission_classes = [IsAuthenticated]

    def get(self, request, student_profile_id):
        attempts = AttemptService.get_attempts_for_student(student_profile_id)
        serializer = AttemptListSerializer(attempts, many=True)
        return ApiResponse.success(
            serializer.data,
            f'{attempts.count()} attempts found.',
        )


class ManualGradeAnswerView(APIView):
    """Lecturer manually grades a short_answer or essay response."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, answer_id):
        serializer = ManualGradeSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.error('Validation failed.', serializer.errors)
        try:
            answer = AttemptService.manual_grade_answer(
                answer_id=answer_id,
                marks=serializer.validated_data['marks'],
                grader=request.user,
            )
        except Exception as e:
            return ApiResponse.error(str(e))
        return ApiResponse.success(
            {'answer_id': str(answer.id), 'marks_obtained': str(answer.marks_obtained)},
            'Answer graded successfully.',
        )
