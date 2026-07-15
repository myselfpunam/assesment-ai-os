from django.urls import path
from .views import (
    AssessmentSummaryView,
    AssessmentLeaderboardView,
    StudentReportView,
    SectionReportView,
)

urlpatterns = [
    # Assessment analytics
    path('assessments/<uuid:assessment_id>/summary/', AssessmentSummaryView.as_view(), name='assessment-summary'),
    path('assessments/<uuid:assessment_id>/leaderboard/', AssessmentLeaderboardView.as_view(), name='assessment-leaderboard'),

    # Student report
    path('students/<uuid:student_profile_id>/report/', StudentReportView.as_view(), name='student-report'),

    # Section / class analytics
    path('sections/<uuid:section_id>/report/', SectionReportView.as_view(), name='section-report'),
]
