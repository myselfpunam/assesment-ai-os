from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.utils.response import ApiResponse
from core.permissions.role_permissions import IsSuperAdminOrUniversityAdmin

from .serializers import (
    DepartmentListSerializer, DepartmentDetailSerializer,
    CreateDepartmentSerializer, UpdateDepartmentSerializer,
    ProgrammeListSerializer, ProgrammeDetailSerializer, CreateProgrammeSerializer,
    AcademicLevelSerializer, AcademicLevelListSerializer, CreateAcademicLevelSerializer,
    SemesterSerializer, CreateSemesterSerializer,
)
from .services import DepartmentService, ProgrammeService, AcademicLevelService, SemesterService


# ── Departments ───────────────────────────────────────────────────────────────

@extend_schema(tags=['Departments'])
class DepartmentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='List departments of a university')
    def get(self, request, university_id):
        departments = DepartmentService.get_departments(university_id, request.user)
        serializer = DepartmentListSerializer(departments, many=True)
        return ApiResponse.success(data=serializer.data, message=f'{departments.count()} departments found.')

    @extend_schema(summary='Create a department', request=CreateDepartmentSerializer)
    def post(self, request, university_id):
        serializer = CreateDepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dept = DepartmentService.create_department(
            university_id=university_id,
            data=serializer.validated_data,
            requesting_user=request.user,
        )
        return ApiResponse.created(
            data=DepartmentDetailSerializer(dept).data,
            message='Department created successfully.'
        )


@extend_schema(tags=['Departments'])
class DepartmentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Get department detail with programmes')
    def get(self, request, department_id):
        dept = DepartmentService.get_department(department_id, request.user)
        return ApiResponse.success(data=DepartmentDetailSerializer(dept).data)

    @extend_schema(summary='Update department', request=UpdateDepartmentSerializer)
    def patch(self, request, department_id):
        serializer = UpdateDepartmentSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        dept = DepartmentService.update_department(department_id, serializer.validated_data, request.user)
        return ApiResponse.success(data=DepartmentDetailSerializer(dept).data, message='Department updated.')

    @extend_schema(summary='Delete department (soft delete)')
    def delete(self, request, department_id):
        DepartmentService.delete_department(department_id, request.user)
        return ApiResponse.success(message='Department deleted.')


# ── Programmes ────────────────────────────────────────────────────────────────

@extend_schema(tags=['Programmes'])
class ProgrammeListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='List programmes in a department')
    def get(self, request, department_id):
        programmes = ProgrammeService.get_programmes(department_id, request.user)
        serializer = ProgrammeListSerializer(programmes, many=True)
        return ApiResponse.success(data=serializer.data)

    @extend_schema(summary='Create a programme', request=CreateProgrammeSerializer)
    def post(self, request, department_id):
        serializer = CreateProgrammeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prog = ProgrammeService.create_programme(
            department_id=department_id,
            data=serializer.validated_data,
            requesting_user=request.user,
        )
        return ApiResponse.created(
            data=ProgrammeDetailSerializer(prog).data,
            message='Programme created successfully.'
        )


@extend_schema(tags=['Programmes'])
class ProgrammeDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Get programme detail with academic levels')
    def get(self, request, programme_id):
        prog = ProgrammeService.get_programme(programme_id, request.user)
        return ApiResponse.success(data=ProgrammeDetailSerializer(prog).data)

    @extend_schema(summary='Update programme')
    def patch(self, request, programme_id):
        serializer = CreateProgrammeSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        prog = ProgrammeService.update_programme(programme_id, serializer.validated_data, request.user)
        return ApiResponse.success(data=ProgrammeDetailSerializer(prog).data, message='Programme updated.')

    @extend_schema(summary='Delete programme (soft delete)')
    def delete(self, request, programme_id):
        ProgrammeService.delete_programme(programme_id, request.user)
        return ApiResponse.success(message='Programme deleted.')


# ── Academic Levels ───────────────────────────────────────────────────────────

@extend_schema(tags=['Academic Levels'])
class AcademicLevelListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='List academic levels in a programme')
    def get(self, request, programme_id):
        levels = AcademicLevelService.get_levels(programme_id, request.user)
        serializer = AcademicLevelListSerializer(levels, many=True)
        return ApiResponse.success(data=serializer.data)

    @extend_schema(summary='Create an academic level', request=CreateAcademicLevelSerializer)
    def post(self, request, programme_id):
        serializer = CreateAcademicLevelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        level = AcademicLevelService.create_level(
            programme_id=programme_id,
            data=serializer.validated_data,
            requesting_user=request.user,
        )
        return ApiResponse.created(
            data=AcademicLevelSerializer(level).data,
            message='Academic Level created successfully.'
        )


@extend_schema(tags=['Academic Levels'])
class AcademicLevelDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Get academic level with semesters')
    def get(self, request, level_id):
        level = AcademicLevelService.get_level(level_id, request.user)
        return ApiResponse.success(data=AcademicLevelSerializer(level).data)

    @extend_schema(summary='Delete academic level')
    def delete(self, request, level_id):
        AcademicLevelService.delete_level(level_id, request.user)
        return ApiResponse.success(message='Academic Level deleted.')


# ── Semesters ─────────────────────────────────────────────────────────────────

@extend_schema(tags=['Semesters'])
class SemesterListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='List semesters in an academic level')
    def get(self, request, level_id):
        semesters = SemesterService.get_semesters(level_id, request.user)
        serializer = SemesterSerializer(semesters, many=True)
        return ApiResponse.success(data=serializer.data)

    @extend_schema(summary='Create a semester', request=CreateSemesterSerializer)
    def post(self, request, level_id):
        serializer = CreateSemesterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        semester = SemesterService.create_semester(
            level_id=level_id,
            data=serializer.validated_data,
            requesting_user=request.user,
        )
        return ApiResponse.created(
            data=SemesterSerializer(semester).data,
            message='Semester created successfully.'
        )


@extend_schema(tags=['Semesters'])
class SemesterDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Delete semester')
    def delete(self, request, semester_id):
        SemesterService.delete_semester(semester_id, request.user)
        return ApiResponse.success(message='Semester deleted.')
