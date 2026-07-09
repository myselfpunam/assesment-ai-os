from django.urls import path
from .views import (
    DepartmentDetailView,
    ProgrammeListCreateView, ProgrammeDetailView,
    AcademicLevelListCreateView, AcademicLevelDetailView,
    SemesterListCreateView, SemesterDeleteView,
)

urlpatterns = [
    # Department detail/update/delete
    path('departments/<uuid:department_id>/', DepartmentDetailView.as_view(), name='department-detail'),

    # Programmes (scoped to department)
    path('departments/<uuid:department_id>/programmes/', ProgrammeListCreateView.as_view(), name='programme-list-create'),
    path('programmes/<uuid:programme_id>/', ProgrammeDetailView.as_view(), name='programme-detail'),

    # Academic Levels (scoped to programme)
    path('programmes/<uuid:programme_id>/levels/', AcademicLevelListCreateView.as_view(), name='level-list-create'),
    path('levels/<uuid:level_id>/', AcademicLevelDetailView.as_view(), name='level-detail'),

    # Semesters (scoped to academic level)
    path('levels/<uuid:level_id>/semesters/', SemesterListCreateView.as_view(), name='semester-list-create'),
    path('semesters/<uuid:semester_id>/', SemesterDeleteView.as_view(), name='semester-delete'),
]
