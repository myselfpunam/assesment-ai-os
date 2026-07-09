from django.urls import path
from .views import (
    UniversityListCreateView,
    UniversityDetailView,
    UniversitySettingsView,
    UniversityAdminListView,
    UniversityAdminRemoveView,
)
from apps.academic.views import (
    DepartmentListCreateView,
    ProgrammeListCreateView,
    AcademicLevelListCreateView,
    SemesterListCreateView,
)
from apps.courses.views import CourseListCreateView

urlpatterns = [
    # Universities CRUD
    path('', UniversityListCreateView.as_view(), name='university-list-create'),
    path('<uuid:university_id>/', UniversityDetailView.as_view(), name='university-detail'),

    # University Settings
    path('<uuid:university_id>/settings/', UniversitySettingsView.as_view(), name='university-settings'),

    # Admin Management
    path('<uuid:university_id>/admins/', UniversityAdminListView.as_view(), name='university-admin-list'),
    path('<uuid:university_id>/admins/<uuid:user_id>/', UniversityAdminRemoveView.as_view(), name='university-admin-remove'),

    # Academic hierarchy (university-scoped list/create)
    path('<uuid:university_id>/departments/', DepartmentListCreateView.as_view(), name='department-list-create'),

    # Courses (scoped to department)
    path('<uuid:university_id>/departments/<uuid:department_id>/courses/', CourseListCreateView.as_view(), name='course-list-create'),
]
