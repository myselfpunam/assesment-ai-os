from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.utils.response import ApiResponse
from core.permissions.role_permissions import IsSuperAdminOrUniversityAdmin

from .models import CourseSection
from .serializers import (
    CourseListSerializer, CourseDetailSerializer,
    CreateCourseSerializer, UpdateCourseSerializer,
    CourseSectionListSerializer, CourseSectionDetailSerializer,
    CreateCourseSectionSerializer, UpdateCourseSectionSerializer,
    AssignLecturerSerializer, LecturerAssignmentSerializer,
    CourseMaterialSerializer, CourseMaterialUploadSerializer,
)
from .services import CourseService, CourseSectionService, CourseMaterialService


# ── Courses ───────────────────────────────────────────────────────────────────

@extend_schema(tags=['Courses'])
class CourseListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='List courses in a department')
    def get(self, request, university_id, department_id):
        courses = CourseService.get_courses(department_id, request.user)
        serializer = CourseListSerializer(courses, many=True)
        return ApiResponse.success(data=serializer.data, message=f'{courses.count()} courses found.')

    @extend_schema(summary='Create a course in a department', request=CreateCourseSerializer)
    def post(self, request, university_id, department_id):
        serializer = CreateCourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = CourseService.create_course(
            department_id=department_id,
            data=serializer.validated_data,
            requesting_user=request.user,
        )
        return ApiResponse.created(
            data=CourseDetailSerializer(course).data,
            message='Course created successfully.'
        )


@extend_schema(tags=['Courses'])
class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Get course detail')
    def get(self, request, course_id):
        course = CourseService.get_course(course_id, request.user)
        return ApiResponse.success(data=CourseDetailSerializer(course).data)

    @extend_schema(summary='Update course', request=UpdateCourseSerializer)
    def patch(self, request, course_id):
        serializer = UpdateCourseSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        course = CourseService.update_course(course_id, serializer.validated_data, request.user)
        return ApiResponse.success(data=CourseDetailSerializer(course).data, message='Course updated.')

    @extend_schema(summary='Delete course (soft delete)')
    def delete(self, request, course_id):
        CourseService.delete_course(course_id, request.user)
        return ApiResponse.success(message='Course deleted.')


# ── Course Sections ───────────────────────────────────────────────────────────

@extend_schema(tags=['Course Sections'])
class CourseSectionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='List sections of a course')
    def get(self, request, course_id):
        sections = CourseSectionService.get_sections(course_id, request.user)
        serializer = CourseSectionListSerializer(sections, many=True)
        return ApiResponse.success(data=serializer.data, message=f'{sections.count()} sections found.')

    @extend_schema(summary='Create a course section', request=CreateCourseSectionSerializer)
    def post(self, request, course_id):
        serializer = CreateCourseSectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        section = CourseSectionService.create_section(
            course_id=course_id,
            data=dict(serializer.validated_data),
            requesting_user=request.user,
        )
        return ApiResponse.created(
            data=CourseSectionDetailSerializer(section).data,
            message='Section created successfully.'
        )


@extend_schema(tags=['Course Sections'])
class CourseSectionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Get section detail with assigned lecturers')
    def get(self, request, section_id):
        section = CourseSectionService.get_section(section_id, request.user)
        return ApiResponse.success(data=CourseSectionDetailSerializer(section).data)

    @extend_schema(summary='Update section', request=UpdateCourseSectionSerializer)
    def patch(self, request, section_id):
        serializer = UpdateCourseSectionSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        section = CourseSectionService.update_section(section_id, serializer.validated_data, request.user)
        return ApiResponse.success(data=CourseSectionDetailSerializer(section).data, message='Section updated.')

    @extend_schema(summary='Delete section (soft delete)')
    def delete(self, request, section_id):
        CourseSectionService.delete_section(section_id, request.user)
        return ApiResponse.success(message='Section deleted.')


# ── Lecturer Assignment ───────────────────────────────────────────────────────

@extend_schema(tags=['Course Sections'])
class AssignLecturerView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Assign a lecturer to a section', request=AssignLecturerSerializer)
    def post(self, request, section_id):
        serializer = AssignLecturerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = CourseSectionService.assign_lecturer(
            section_id=section_id,
            lecturer_id=serializer.validated_data['lecturer_id'],
            requesting_user=request.user,
        )
        return ApiResponse.created(
            data=LecturerAssignmentSerializer(assignment).data,
            message='Lecturer assigned successfully.'
        )


@extend_schema(tags=['Course Sections'])
class RemoveLecturerView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Remove a lecturer from a section')
    def delete(self, request, section_id, lecturer_id):
        CourseSectionService.remove_lecturer(section_id, lecturer_id, request.user)
        return ApiResponse.success(message='Lecturer removed from section.')


# ── Course Materials ──────────────────────────────────────────────────────────

@extend_schema(tags=['Course Materials'])
class CourseMaterialListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='List all materials for a section')
    def get(self, request, section_id):
        materials = CourseMaterialService.get_materials(section_id)
        serializer = CourseMaterialSerializer(materials, many=True)
        return ApiResponse.success(serializer.data, f'{materials.count()} materials found.')

    @extend_schema(summary='Upload a material to a section')
    def post(self, request, section_id):
        serializer = CourseMaterialUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.error('Validation failed.', serializer.errors)

        try:
            material = CourseMaterialService.upload_material(
                section_id=section_id,
                user=request.user,
                title=serializer.validated_data['title'],
                file=serializer.validated_data['file'],
            )
        except ValueError as e:
            return ApiResponse.error(str(e))
        except Exception as e:
            return ApiResponse.error(f'Upload failed: {str(e)}')

        return ApiResponse.created(
            CourseMaterialSerializer(material).data,
            'Material uploaded successfully. Text extracted and ready for AI quiz generation.',
        )


@extend_schema(tags=['Course Materials'])
class CourseMaterialDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Delete a material')
    def delete(self, request, material_id):
        CourseMaterialService.delete_material(material_id)
        return ApiResponse.success(None, 'Material deleted successfully.')


@extend_schema(tags=['Course Sections'])
class SectionStudentsView(APIView):
    """
    List all students enrolled in a section.
    Used by lecturers to see their class roster.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        from django.shortcuts import get_object_or_404
        from apps.students.models import Enrollment

        section = get_object_or_404(CourseSection, id=section_id, deleted_at__isnull=True)

        enrollments = Enrollment.objects.filter(
            section=section,
            deleted_at__isnull=True,
        ).select_related(
            'student__user', 'student__batch', 'student__programme'
        ).order_by('student__student_id')

        students_data = []
        for e in enrollments:
            sp = e.student
            students_data.append({
                'enrollment_id': str(e.id),
                'student_profile_id': str(sp.id),
                'student_id': sp.student_id,
                'full_name': sp.user.get_full_name(),
                'email': sp.user.email,
                'batch': sp.batch.name if sp.batch else None,
                'programme': sp.programme.name if sp.programme else None,
                'enrollment_status': e.status,
                'grade': e.grade,
                'enrolled_at': e.created_at,
            })

        return ApiResponse.success(
            {
                'section': f"{section.course.name} — {section.section_code}",
                'total_students': len(students_data),
                'students': students_data,
            },
            f'{len(students_data)} students in this section.',
        )
