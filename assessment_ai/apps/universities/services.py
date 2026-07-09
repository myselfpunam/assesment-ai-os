import logging
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from .models import University, UniversitySettings, UniversityAdmin

logger = logging.getLogger(__name__)
User = get_user_model()


def _default_grading_scale():
    return {'A': 90, 'B': 80, 'C': 70, 'D': 60, 'F': 0}


class UniversityService:
    """
    All university business logic lives here.
    Views call this service — never put logic in views.
    """

    # ── Queries ──────────────────────────────────────────────────────────────

    @staticmethod
    def get_all_universities(requesting_user):
        """Super Admin sees all. University Admin sees only their own."""
        if requesting_user.is_super_admin:
            return University.objects.select_related('settings', 'created_by').all()

        if requesting_user.is_university_admin:
            return University.objects.select_related('settings', 'created_by').filter(
                admins__user=requesting_user,
                admins__deleted_at__isnull=True,
            )

        raise PermissionDenied('You do not have permission to view universities.')

    @staticmethod
    def get_university_by_id(university_id):
        try:
            return University.objects.select_related('settings', 'created_by').get(
                id=university_id,
                deleted_at__isnull=True,
            )
        except University.DoesNotExist:
            raise NotFound(f'University not found.')

    @staticmethod
    def get_university_for_user(user):
        """
        Returns the university associated with a university_admin user.
        Used when building JWT token claims and for tenant resolution.
        """
        profile = UniversityAdmin.objects.select_related('university').filter(
            user=user,
            deleted_at__isnull=True,
        ).first()
        return profile.university if profile else None

    # ── Create ───────────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def create_university(data: dict, requesting_user) -> University:
        """
        Only Super Admin can create a university.
        UniversitySettings is auto-created with defaults.
        """
        if not requesting_user.is_super_admin:
            raise PermissionDenied('Only Super Admins can create universities.')

        university = University(
            name=data['name'],
            website=data.get('website', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            city=data.get('city', ''),
            country=data.get('country', ''),
            timezone=data.get('timezone', 'UTC'),
            created_by=requesting_user,
        )
        if data.get('logo'):
            university.logo = data['logo']
        university.save()

        # Auto-create default settings for this university
        UniversitySettings.objects.create(
            university=university,
            grading_scale=_default_grading_scale(),
        )

        logger.info(f"University created: {university.name} by {requesting_user.email}")
        return university

    # ── Update ───────────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def update_university(university_id, data: dict, requesting_user) -> University:
        university = UniversityService.get_university_by_id(university_id)

        # Super Admin can update any. University Admin can only update their own.
        if not requesting_user.is_super_admin:
            is_admin = UniversityAdmin.objects.filter(
                university=university,
                user=requesting_user,
                deleted_at__isnull=True,
            ).exists()
            if not is_admin:
                raise PermissionDenied('You can only update universities you manage.')

        for field in ['website', 'email', 'phone', 'address', 'city', 'country', 'timezone', 'is_active']:
            if field in data:
                setattr(university, field, data[field])
        if data.get('logo'):
            university.logo = data['logo']

        university.save()
        logger.info(f"University updated: {university.name} by {requesting_user.email}")
        return university

    # ── Delete ───────────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def delete_university(university_id, requesting_user):
        if not requesting_user.is_super_admin:
            raise PermissionDenied('Only Super Admins can delete universities.')

        university = UniversityService.get_university_by_id(university_id)
        university.soft_delete()
        logger.info(f"University soft-deleted: {university.name} by {requesting_user.email}")

    # ── Settings ─────────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def update_settings(university_id, data: dict, requesting_user) -> UniversitySettings:
        university = UniversityService.get_university_by_id(university_id)

        if not requesting_user.is_super_admin:
            is_admin = UniversityAdmin.objects.filter(
                university=university,
                user=requesting_user,
                deleted_at__isnull=True,
            ).exists()
            if not is_admin:
                raise PermissionDenied('You can only manage settings for universities you administer.')

        settings = university.settings
        updatable_fields = [
            'max_students', 'max_lecturers', 'max_departments',
            'allow_ai_generation', 'ai_questions_per_quiz', 'ai_model_preference',
            'allow_student_self_registration', 'academic_year_start_month',
            'default_language', 'grading_scale', 'allow_late_submission', 'max_quiz_attempts',
        ]
        for field in updatable_fields:
            if field in data:
                setattr(settings, field, data[field])
        settings.save()
        logger.info(f"Settings updated for university: {university.name}")
        return settings

    # ── Admin Assignment ──────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def assign_admin(university_id, user_id, is_primary: bool, requesting_user) -> UniversityAdmin:
        """
        Only Super Admin can assign a university admin.
        The user being assigned must have the university_admin role.
        """
        if not requesting_user.is_super_admin:
            raise PermissionDenied('Only Super Admins can assign university admins.')

        university = UniversityService.get_university_by_id(university_id)

        try:
            user = User.objects.get(id=user_id, deleted_at__isnull=True)
        except User.DoesNotExist:
            raise NotFound('User not found.')

        if not user.is_university_admin:
            raise ValidationError({
                'user_id': 'This user does not have the University Admin role. '
                           'Change their role first.'
            })

        if UniversityAdmin.objects.filter(university=university, user=user).exists():
            raise ValidationError({'user_id': 'This user is already an admin of this university.'})

        # If setting as primary, demote existing primary
        if is_primary:
            UniversityAdmin.objects.filter(
                university=university,
                is_primary=True,
                deleted_at__isnull=True,
            ).update(is_primary=False)

        admin_profile = UniversityAdmin.objects.create(
            university=university,
            user=user,
            is_primary=is_primary,
            assigned_by=requesting_user,
        )

        logger.info(
            f"Admin assigned: {user.email} → {university.name} "
            f"(primary={is_primary}) by {requesting_user.email}"
        )
        return admin_profile

    @staticmethod
    @transaction.atomic
    def remove_admin(university_id, user_id, requesting_user):
        if not requesting_user.is_super_admin:
            raise PermissionDenied('Only Super Admins can remove university admins.')

        try:
            admin_profile = UniversityAdmin.objects.get(
                university_id=university_id,
                user_id=user_id,
                deleted_at__isnull=True,
            )
        except UniversityAdmin.DoesNotExist:
            raise NotFound('Admin assignment not found.')

        admin_profile.soft_delete()
        logger.info(f"Admin removed from university_id={university_id}, user_id={user_id}")

    @staticmethod
    def get_admins(university_id):
        return UniversityAdmin.objects.select_related('user', 'user__role').filter(
            university_id=university_id,
            deleted_at__isnull=True,
        )
