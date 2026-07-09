from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.utils.response import ApiResponse
from core.permissions.role_permissions import IsSuperAdminOrUniversityAdmin

from .serializers import (
    BatchSerializer, CreateBatchSerializer, UpdateBatchSerializer,
    StudentProfileListSerializer, StudentProfileDetailSerializer, CreateStudentProfileSerializer,
    EnrollmentSerializer, CreateEnrollmentSerializer, UpdateEnrollmentSerializer,
)
from .services import BatchService, StudentService, EnrollmentService


# ── Batches ───────────────────────────────────────────────────────────────────

@extend_schema(tags=['Batches'])
class BatchListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='List all batches')
    def get(self, request):
        programme_id = request.query_params.get('programme_id')
        batches = BatchService.get_batches(request.user, programme_id=programme_id)
        serializer = BatchSerializer(batches, many=True)
        return ApiResponse.success(data=serializer.data, message=f'{batches.count()} batches found.')

    @extend_schema(summary='Create a batch', request=CreateBatchSerializer)
    def post(self, request):
        serializer = CreateBatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        batch = BatchService.create_batch(serializer.validated_data, request.user)
        return ApiResponse.created(
            data=BatchSerializer(batch).data,
            message='Batch created successfully.'
        )


@extend_schema(tags=['Batches'])
class BatchDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Get batch detail')
    def get(self, request, batch_id):
        batch = BatchService.get_batch(batch_id, request.user)
        return ApiResponse.success(data=BatchSerializer(batch).data)

    @extend_schema(summary='Update batch', request=UpdateBatchSerializer)
    def patch(self, request, batch_id):
        serializer = UpdateBatchSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        batch = BatchService.update_batch(batch_id, dict(serializer.validated_data), request.user)
        return ApiResponse.success(data=BatchSerializer(batch).data, message='Batch updated.')

    @extend_schema(summary='Delete batch (soft delete)')
    def delete(self, request, batch_id):
        BatchService.delete_batch(batch_id, request.user)
        return ApiResponse.success(message='Batch deleted.')


# ── Students ──────────────────────────────────────────────────────────────────

@extend_schema(tags=['Students'])
class StudentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='List all student profiles')
    def get(self, request):
        programme_id = request.query_params.get('programme_id')
        batch_id = request.query_params.get('batch_id')
        students = StudentService.get_students(request.user, programme_id=programme_id, batch_id=batch_id)
        serializer = StudentProfileListSerializer(students, many=True)
        return ApiResponse.success(data=serializer.data, message=f'{students.count()} students found.')

    @extend_schema(summary='Create a student profile', request=CreateStudentProfileSerializer)
    def post(self, request):
        serializer = CreateStudentProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = StudentService.create_student(serializer.validated_data, request.user)
        return ApiResponse.created(
            data=StudentProfileDetailSerializer(student).data,
            message='Student profile created successfully.'
        )


@extend_schema(tags=['Students'])
class StudentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Get student profile detail')
    def get(self, request, student_id):
        student = StudentService.get_student(student_id, request.user)
        return ApiResponse.success(data=StudentProfileDetailSerializer(student).data)

    @extend_schema(summary='Update student profile')
    def patch(self, request, student_id):
        serializer = CreateStudentProfileSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        student = StudentService.update_student(student_id, dict(serializer.validated_data), request.user)
        return ApiResponse.success(data=StudentProfileDetailSerializer(student).data, message='Student updated.')


# ── Enrollments ───────────────────────────────────────────────────────────────

@extend_schema(tags=['Enrollments'])
class EnrollmentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='List enrollments (filter by ?section_id= or ?student_id=)')
    def get(self, request):
        section_id = request.query_params.get('section_id')
        student_id = request.query_params.get('student_id')
        enrollments = EnrollmentService.get_enrollments(section_id=section_id, student_id=student_id)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return ApiResponse.success(data=serializer.data, message=f'{enrollments.count()} enrollments found.')

    @extend_schema(summary='Enroll a student in a section', request=CreateEnrollmentSerializer)
    def post(self, request):
        serializer = CreateEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = EnrollmentService.enroll_student(serializer.validated_data, request.user)
        return ApiResponse.created(
            data=EnrollmentSerializer(enrollment).data,
            message='Student enrolled successfully.'
        )


@extend_schema(tags=['Enrollments'])
class EnrollmentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Update enrollment status or grade', request=UpdateEnrollmentSerializer)
    def patch(self, request, enrollment_id):
        serializer = UpdateEnrollmentSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        enrollment = EnrollmentService.update_enrollment(enrollment_id, serializer.validated_data, request.user)
        return ApiResponse.success(data=EnrollmentSerializer(enrollment).data, message='Enrollment updated.')

    @extend_schema(summary='Drop a student from a section')
    def delete(self, request, enrollment_id):
        enrollment = EnrollmentService.drop_enrollment(enrollment_id, request.user)
        return ApiResponse.success(data=EnrollmentSerializer(enrollment).data, message='Student dropped from section.')


@extend_schema(tags=['Students'])
class StudentEnrolledCoursesView(APIView):
    """
    All courses a student is enrolled in — with course name, section,
    semester, grade and status. Frontend student profile page.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        from django.shortcuts import get_object_or_404
        from .models import StudentProfile, Enrollment

        student = get_object_or_404(StudentProfile, id=student_id, deleted_at__isnull=True)

        enrollments = Enrollment.objects.filter(
            student=student,
            deleted_at__isnull=True,
        ).select_related(
            'section__course', 'section__semester',
            'section__course__department__university',
        ).order_by('-created_at')

        courses_data = []
        for e in enrollments:
            sec = e.section
            courses_data.append({
                'enrollment_id': str(e.id),
                'course_name': sec.course.name,
                'course_code': sec.course.code,
                'credit_hours': sec.course.credit_hours,
                'section_code': sec.section_code,
                'semester': sec.semester.name,
                'university': sec.course.department.university.name,
                'department': sec.course.department.name,
                'status': e.status,
                'grade': e.grade,
                'enrolled_at': e.created_at,
            })

        return ApiResponse.success(
            {
                'student': {
                    'id': str(student.id),
                    'student_id': student.student_id,
                    'name': student.user.get_full_name(),
                    'email': student.user.email,
                    'programme': student.programme.name,
                    'batch': student.batch.name if student.batch else None,
                },
                'total_enrolled': len(courses_data),
                'courses': courses_data,
            },
            f'{len(courses_data)} enrolled courses retrieved.',
        )


@extend_schema(tags=['Students'])
class StudentAssessmentsView(APIView):
    """
    All published assessments available to a student
    based on the sections they are enrolled in.
    Frontend student dashboard — shows upcoming quizzes/exams.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        from django.shortcuts import get_object_or_404
        from .models import StudentProfile, Enrollment
        from apps.assessments.models import Assessment

        student = get_object_or_404(StudentProfile, id=student_id, deleted_at__isnull=True)

        section_ids = Enrollment.objects.filter(
            student=student,
            status='enrolled',
            deleted_at__isnull=True,
        ).values_list('section_id', flat=True)

        assessments = Assessment.objects.filter(
            section_id__in=section_ids,
            is_published=True,
            is_active=True,
            deleted_at__isnull=True,
        ).select_related('section__course', 'section__semester').order_by('end_datetime')

        assessments_data = []
        for a in assessments:
            assessments_data.append({
                'assessment_id': str(a.id),
                'title': a.title,
                'assessment_type': a.assessment_type,
                'course_name': a.section.course.name,
                'course_code': a.section.course.code,
                'section_code': a.section.section_code,
                'semester': a.section.semester.name,
                'total_marks': a.total_marks,
                'pass_marks': a.pass_marks,
                'duration_minutes': a.duration_minutes,
                'start_datetime': a.start_datetime,
                'end_datetime': a.end_datetime,
                'allow_multiple_attempts': a.allow_multiple_attempts,
                'max_attempts': a.max_attempts,
            })

        return ApiResponse.success(
            {
                'student': {
                    'id': str(student.id),
                    'name': student.user.get_full_name(),
                    'student_id': student.student_id,
                },
                'total_assessments': len(assessments_data),
                'assessments': assessments_data,
            },
            f'{len(assessments_data)} assessments available.',
        )
