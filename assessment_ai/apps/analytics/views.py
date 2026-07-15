from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from core.utils.response import ApiResponse
from .services import (
    AssessmentAnalyticsService,
    StudentAnalyticsService,
    SectionAnalyticsService,
)


class AssessmentSummaryView(APIView):
    """
    Full statistics for one assessment:
    pass rate, average score, score distribution, grading status.
    Use on: Assessment results page (lecturer view).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id):
        data = AssessmentAnalyticsService.get_assessment_summary(assessment_id)
        return ApiResponse.success(data, 'Assessment analytics retrieved.')


class AssessmentLeaderboardView(APIView):
    """
    Top performers for an assessment ranked by score.
    Use on: Leaderboard / results page.
    Optional query param: ?limit=10
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id):
        limit = int(request.query_params.get('limit', 10))
        data = AssessmentAnalyticsService.get_leaderboard(assessment_id, limit=limit)
        return ApiResponse.success(data, 'Leaderboard retrieved.')


class StudentReportView(APIView):
    """
    A student's full performance report across all their assessments.
    Use on: Student profile — Performance tab.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, student_profile_id):
        data = StudentAnalyticsService.get_student_report(student_profile_id)
        return ApiResponse.success(data, 'Student report retrieved.')


class SectionReportView(APIView):
    """
    Analytics for an entire class section:
    enrolled students, per-assessment stats, top 5 performers.
    Use on: Lecturer's class analytics dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        data = SectionAnalyticsService.get_section_report(section_id)
        return ApiResponse.success(data, 'Section report retrieved.')
