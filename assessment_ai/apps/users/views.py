from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from core.utils.response import ApiResponse
from core.permissions.role_permissions import IsSuperAdmin

from .serializers import (
    UserListSerializer,
    UserDetailSerializer,
    CreateUserSerializer,
    UpdateUserSerializer,
    ChangePasswordSerializer,
    LecturerProfileSerializer,
)
from .services import UserService


@extend_schema(tags=['Users'])
class UserListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(summary='List all users', description='Super Admin only. Supports ?role=lecturer&search=john filters.')
    def get(self, request):
        filters = {
            'role': request.query_params.get('role'),
            'is_active': request.query_params.get('is_active'),
            'search': request.query_params.get('search'),
        }
        users = UserService.get_all_users(request.user, filters=filters)
        serializer = UserListSerializer(users, many=True)
        return ApiResponse.success(
            data=serializer.data,
            message=f'{len(serializer.data)} users retrieved.'
        )

    @extend_schema(summary='Create a user', request=CreateUserSerializer)
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.create_user(
            data=serializer.validated_data,
            requesting_user=request.user,
        )
        return ApiResponse.created(
            data=UserDetailSerializer(user).data,
            message='User created successfully.'
        )


@extend_schema(tags=['Users'])
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = UserService.get_user_by_id(user_id)
        serializer = UserDetailSerializer(user)
        return ApiResponse.success(data=serializer.data)

    def patch(self, request, user_id):
        serializer = UpdateUserSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = UserService.update_user(
            user_id=user_id,
            data=serializer.validated_data,
            requesting_user=request.user,
        )
        return ApiResponse.success(
            data=UserDetailSerializer(user).data,
            message='User updated successfully.'
        )

    def delete(self, request, user_id):
        UserService.soft_delete_user(user_id=user_id, requesting_user=request.user)
        return ApiResponse.success(message='User deleted successfully.')


@extend_schema(tags=['Users'])
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return ApiResponse.success(data=serializer.data)

    def patch(self, request):
        serializer = UpdateUserSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = UserService.update_user(
            user_id=str(request.user.id),
            data=serializer.validated_data,
            requesting_user=request.user,
        )
        return ApiResponse.success(
            data=UserDetailSerializer(user).data,
            message='Profile updated successfully.'
        )


@extend_schema(tags=['Users'])
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserService.change_password(
            user=request.user,
            current_password=serializer.validated_data['current_password'],
            new_password=serializer.validated_data['new_password'],
        )
        return ApiResponse.success(message='Password changed successfully.')


@extend_schema(tags=['Users'])
class LecturerProfileView(APIView):
    """
    Full profile for a lecturer — their info + all sections they teach
    + student count + assessment count per section.
    Frontend can build a complete Lecturer Dashboard from this single call.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, lecturer_id):
        from apps.users.models import User
        from django.shortcuts import get_object_or_404
        lecturer = get_object_or_404(User, id=lecturer_id, deleted_at__isnull=True)
        serializer = LecturerProfileSerializer(lecturer)
        return ApiResponse.success(serializer.data, 'Lecturer profile retrieved successfully.')
