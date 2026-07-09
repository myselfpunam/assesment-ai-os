from rest_framework.permissions import BasePermission
from .models import UniversityAdmin


class IsUniversityAdminOfThisUniversity(BasePermission):
    """
    Checks that the requesting user is an admin of the specific university
    being accessed (object-level permission).
    """
    message = 'You are not an admin of this university.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin:
            return True
        return UniversityAdmin.objects.filter(
            university=obj,
            user=request.user,
            deleted_at__isnull=True,
        ).exists()
