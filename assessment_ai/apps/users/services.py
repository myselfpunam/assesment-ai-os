import logging
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from apps.roles.models import Role, RoleChoices

logger = logging.getLogger(__name__)
User = get_user_model()


class UserService:
    """
    All user-related business logic lives here.
    Views MUST NOT contain business logic — only call this service.
    """

    @staticmethod
    def get_all_users(requesting_user, filters=None):
        """Super admin sees all users. University admin sees users in their tenant (Phase 2)."""
        if not requesting_user.is_super_admin:
            raise PermissionDenied('You do not have permission to list all users.')
        qs = User.objects.select_related('role').filter(deleted_at__isnull=True)
        if filters:
            if filters.get('role'):
                qs = qs.filter(role__name=filters['role'])
            if filters.get('is_active') is not None:
                qs = qs.filter(is_active=filters['is_active'])
            if filters.get('search'):
                qs = qs.filter(
                    email__icontains=filters['search']
                ) | qs.filter(
                    first_name__icontains=filters['search']
                ) | qs.filter(
                    last_name__icontains=filters['search']
                )
        return qs

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.objects.select_related('role').get(id=user_id, deleted_at__isnull=True)
        except User.DoesNotExist:
            raise NotFound(f'User with ID {user_id} not found.')

    @staticmethod
    @transaction.atomic
    def create_user(data: dict, requesting_user) -> User:
        """
        Admin creates a new user.
        Business rules:
        - Only super_admin can create university_admin
        - Only super_admin or university_admin can create lecturers/reviewers
        - Email must be unique
        """
        role = data.get('role')

        if role.name == RoleChoices.SUPER_ADMIN and not requesting_user.is_super_admin:
            raise PermissionDenied('Only Super Admins can create another Super Admin.')

        if role.name == RoleChoices.UNIVERSITY_ADMIN and not requesting_user.is_super_admin:
            raise PermissionDenied('Only Super Admins can create University Admins.')

        if User.all_objects.filter(email=data['email']).exists():
            raise ValidationError({'email': 'A user with this email already exists.'})

        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data.get('phone_number', ''),
            role=role,
        )
        user.set_password(data['password'])
        user.save()

        logger.info(f"User created: {user.email} with role {role.name} by {requesting_user.email}")
        return user

    @staticmethod
    @transaction.atomic
    def update_user(user_id: str, data: dict, requesting_user) -> User:
        user = UserService.get_user_by_id(user_id)

        # Users can update their own profile; admins can update anyone
        if str(requesting_user.id) != str(user_id) and not requesting_user.is_super_admin:
            raise PermissionDenied('You can only update your own profile.')

        for field in ['first_name', 'last_name', 'phone_number']:
            if field in data:
                setattr(user, field, data[field])
        user.save()
        return user

    @staticmethod
    @transaction.atomic
    def change_password(user, current_password: str, new_password: str):
        if not user.check_password(current_password):
            raise ValidationError({'current_password': 'Current password is incorrect.'})
        user.set_password(new_password)
        user.save(update_fields=['password', 'updated_at'])
        logger.info(f"Password changed for user: {user.email}")

    @staticmethod
    @transaction.atomic
    def soft_delete_user(user_id: str, requesting_user):
        if not requesting_user.is_super_admin:
            raise PermissionDenied('Only Super Admins can delete users.')
        user = UserService.get_user_by_id(user_id)
        if str(user.id) == str(requesting_user.id):
            raise ValidationError({'detail': 'You cannot delete your own account.'})
        user.soft_delete()
        logger.info(f"User soft-deleted: {user.email} by {requesting_user.email}")
        return user
