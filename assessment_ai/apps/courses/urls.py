from django.urls import path
from .views import (
    CourseDetailView,
    CourseSectionListCreateView, CourseSectionDetailView,
    AssignLecturerView, RemoveLecturerView,
    CourseMaterialListCreateView, CourseMaterialDeleteView,
    SectionStudentsView,
)

urlpatterns = [
    # Course detail/update/delete
    path('<uuid:course_id>/', CourseDetailView.as_view(), name='course-detail'),

    # Sections under a course
    path('<uuid:course_id>/sections/', CourseSectionListCreateView.as_view(), name='section-list-create'),

    # Section detail/update/delete
    path('sections/<uuid:section_id>/', CourseSectionDetailView.as_view(), name='section-detail'),

    # Assign lecturer to a section
    path('sections/<uuid:section_id>/assign-lecturer/', AssignLecturerView.as_view(), name='assign-lecturer'),

    # Remove lecturer from a section
    path('sections/<uuid:section_id>/lecturers/<uuid:lecturer_id>/', RemoveLecturerView.as_view(), name='remove-lecturer'),

    # Course Materials — upload once, use many times for AI quiz
    path('sections/<uuid:section_id>/materials/', CourseMaterialListCreateView.as_view(), name='material-list-create'),
    path('materials/<uuid:material_id>/', CourseMaterialDeleteView.as_view(), name='material-delete'),

    # Students roster for a section (lecturer sees their class)
    path('sections/<uuid:section_id>/students/', SectionStudentsView.as_view(), name='section-students'),
]
