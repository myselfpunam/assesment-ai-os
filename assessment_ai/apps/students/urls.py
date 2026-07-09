from django.urls import path
from .views import (
    BatchListCreateView, BatchDetailView,
    StudentListCreateView, StudentDetailView,
    EnrollmentListCreateView, EnrollmentDetailView,
    StudentEnrolledCoursesView, StudentAssessmentsView,
)

urlpatterns = [
    # Batches
    path('batches/', BatchListCreateView.as_view(), name='batch-list-create'),
    path('batches/<uuid:batch_id>/', BatchDetailView.as_view(), name='batch-detail'),

    # Students
    path('', StudentListCreateView.as_view(), name='student-list-create'),
    path('<uuid:student_id>/', StudentDetailView.as_view(), name='student-detail'),

    # Student profile sub-resources (frontend profile pages)
    path('<uuid:student_id>/enrolled-courses/', StudentEnrolledCoursesView.as_view(), name='student-enrolled-courses'),
    path('<uuid:student_id>/assessments/', StudentAssessmentsView.as_view(), name='student-assessments'),

    # Enrollments
    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment-list-create'),
    path('enrollments/<uuid:enrollment_id>/', EnrollmentDetailView.as_view(), name='enrollment-detail'),
]
