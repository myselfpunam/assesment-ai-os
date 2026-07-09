from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    message = 'Only Super Admins can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role is not None
            and request.user.role.name == 'super_admin'
        )


class IsUniversityAdmin(BasePermission):
    message = 'Only University Admins can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role is not None
            and request.user.role.name == 'university_admin'
        )


class IsLecturer(BasePermission):
    message = 'Only Lecturers can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role is not None
            and request.user.role.name == 'lecturer'
        )


class IsReviewer(BasePermission):
    message = 'Only Reviewers can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role is not None
            and request.user.role.name == 'reviewer'
        )


class IsStudent(BasePermission):
    message = 'Only Students can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role is not None
            and request.user.role.name == 'student'
        )


class IsSuperAdminOrUniversityAdmin(BasePermission):
    message = 'Only Super Admins or University Admins can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role is not None
            and request.user.role.name in ('super_admin', 'university_admin')
        )


class IsAdminUser(BasePermission):
    """Super Admin or University Admin."""
    message = 'Admin access required.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role is not None
            and request.user.role.name in ('super_admin', 'university_admin')
        )
