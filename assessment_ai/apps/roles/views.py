from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from core.utils.response import ApiResponse
from core.permissions.role_permissions import IsSuperAdmin
from .models import Role
from .serializers import RoleSerializer


@extend_schema(tags=['Roles'])
class RoleListView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(summary='List all system roles')
    def get(self, request):
        roles = Role.objects.filter(is_active=True)
        serializer = RoleSerializer(roles, many=True)
        return ApiResponse.success(data=serializer.data, message='Roles retrieved successfully')
