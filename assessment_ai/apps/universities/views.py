from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.utils.response import ApiResponse
from core.permissions.role_permissions import IsSuperAdmin, IsSuperAdminOrUniversityAdmin

from .serializers import (
    UniversityListSerializer,
    UniversityDetailSerializer,
    CreateUniversitySerializer,
    UpdateUniversitySerializer,
    UniversitySettingsSerializer,
    UniversityAdminSerializer,
    AssignAdminSerializer,
)
from .services import UniversityService


@extend_schema(tags=['Universities'])
class UniversityListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(
        summary='List universities',
        description='Super Admin sees all universities. University Admin sees only their own.',
    )
    def get(self, request):
        universities = UniversityService.get_all_universities(request.user)
        serializer = UniversityListSerializer(universities, many=True)
        return ApiResponse.success(
            data=serializer.data,
            message=f'{len(serializer.data)} universities retrieved.'
        )

    @extend_schema(
        summary='Create a university',
        description='Super Admin only. Settings are auto-created with defaults.',
        request=CreateUniversitySerializer,
    )
    def post(self, request):
        serializer = CreateUniversitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        university = UniversityService.create_university(
            data=serializer.validated_data,
            requesting_user=request.user,
        )
        return ApiResponse.created(
            data=UniversityDetailSerializer(university).data,
            message='University created successfully.'
        )


@extend_schema(tags=['Universities'])
class UniversityDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Get university detail')
    def get(self, request, university_id):
        university = UniversityService.get_university_by_id(university_id)
        serializer = UniversityDetailSerializer(university)
        return ApiResponse.success(data=serializer.data)

    @extend_schema(summary='Update university', request=UpdateUniversitySerializer)
    def patch(self, request, university_id):
        serializer = UpdateUniversitySerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        university = UniversityService.update_university(
            university_id=university_id,
            data=serializer.validated_data,
            requesting_user=request.user,
        )
        return ApiResponse.success(
            data=UniversityDetailSerializer(university).data,
            message='University updated successfully.'
        )

    @extend_schema(summary='Delete university (soft delete)', description='Super Admin only.')
    def delete(self, request, university_id):
        UniversityService.delete_university(
            university_id=university_id,
            requesting_user=request.user,
        )
        return ApiResponse.success(message='University deleted successfully.')


@extend_schema(tags=['Universities'])
class UniversitySettingsView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='Get university settings')
    def get(self, request, university_id):
        university = UniversityService.get_university_by_id(university_id)
        serializer = UniversitySettingsSerializer(university.settings)
        return ApiResponse.success(data=serializer.data)

    @extend_schema(summary='Update university settings', request=UniversitySettingsSerializer)
    def patch(self, request, university_id):
        serializer = UniversitySettingsSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        settings = UniversityService.update_settings(
            university_id=university_id,
            data=serializer.validated_data,
            requesting_user=request.user,
        )
        return ApiResponse.success(
            data=UniversitySettingsSerializer(settings).data,
            message='Settings updated successfully.'
        )


@extend_schema(tags=['Universities'])
class UniversityAdminListView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminOrUniversityAdmin]

    @extend_schema(summary='List admins of a university')
    def get(self, request, university_id):
        admins = UniversityService.get_admins(university_id)
        serializer = UniversityAdminSerializer(admins, many=True)
        return ApiResponse.success(data=serializer.data)

    @extend_schema(
        summary='Assign a university admin',
        description='Super Admin only. The user must already have the university_admin role.',
        request=AssignAdminSerializer,
    )
    def post(self, request, university_id):
        serializer = AssignAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin_profile = UniversityService.assign_admin(
            university_id=university_id,
            user_id=serializer.validated_data['user_id'],
            is_primary=serializer.validated_data.get('is_primary', False),
            requesting_user=request.user,
        )
        return ApiResponse.created(
            data=UniversityAdminSerializer(admin_profile).data,
            message='University admin assigned successfully.'
        )


@extend_schema(tags=['Universities'])
class UniversityAdminRemoveView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(summary='Remove a university admin', description='Super Admin only.')
    def delete(self, request, university_id, user_id):
        UniversityService.remove_admin(
            university_id=university_id,
            user_id=user_id,
            requesting_user=request.user,
        )
        return ApiResponse.success(message='Admin removed from university.')
