from django.urls import path
from .views import (
    StartAttemptView,
    SubmitAttemptView,
    AttemptDetailView,
    AssessmentAttemptsView,
    StudentAttemptsView,
    ManualGradeAnswerView,
)

urlpatterns = [
    # Start an attempt on an assessment
    path('assessments/<uuid:assessment_id>/start/', StartAttemptView.as_view(), name='attempt-start'),

    # Submit answers → auto-grade
    path('<uuid:attempt_id>/submit/', SubmitAttemptView.as_view(), name='attempt-submit'),

    # Get attempt detail (student or lecturer)
    path('<uuid:attempt_id>/', AttemptDetailView.as_view(), name='attempt-detail'),

    # Lecturer: all attempts for an assessment
    path('assessments/<uuid:assessment_id>/all/', AssessmentAttemptsView.as_view(), name='assessment-attempts'),

    # Student: all their attempts across assessments
    path('students/<uuid:student_profile_id>/all/', StudentAttemptsView.as_view(), name='student-attempts'),

    # Lecturer: manually grade a short_answer / essay answer
    path('answers/<uuid:answer_id>/grade/', ManualGradeAnswerView.as_view(), name='manual-grade-answer'),
]
