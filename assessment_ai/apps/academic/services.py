import logging
from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from apps.universities.models import UniversityAdmin
from .models import Department, Programme, AcademicLevel, Semester

logger = logging.getLogger(__name__)


def _check_university_access(user, university_id):
    """
    Verifies the user can manage this university's academic structure.
    Super Admin → always allowed.
    University Admin → must be admin of this specific university.
    """
    if user.is_super_admin:
        return True
    if user.is_university_admin:
        has_access = UniversityAdmin.objects.filter(
            user=user,
            university_id=university_id,
            deleted_at__isnull=True,
        ).exists()
        if not has_access:
            raise PermissionDenied('You do not have access to this university.')
        return True
    raise PermissionDenied('You do not have permission to perform this action.')


# ── Department Service ────────────────────────────────────────────────────────

class DepartmentService:

    @staticmethod
    def get_departments(university_id, requesting_user):
        _check_university_access(requesting_user, university_id)
        return Department.objects.filter(
            university_id=university_id,
            deleted_at__isnull=True,
        ).prefetch_related('programmes')

    @staticmethod
    def get_department(department_id, requesting_user):
        try:
            dept = Department.objects.select_related('university').prefetch_related(
                'programmes__academic_levels__semesters'
            ).get(id=department_id, deleted_at__isnull=True)
        except Department.DoesNotExist:
            raise NotFound('Department not found.')
        _check_university_access(requesting_user, dept.university_id)
        return dept

    @staticmethod
    @transaction.atomic
    def create_department(university_id, data: dict, requesting_user) -> Department:
        _check_university_access(requesting_user, university_id)

        if Department.objects.filter(
            university_id=university_id,
            code=data['code'],
            deleted_at__isnull=True,
        ).exists():
            raise ValidationError({'code': f"Department with code '{data['code']}' already exists in this university."})

        dept = Department.objects.create(
            university_id=university_id,
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
        )
        logger.info(f"Department created: {dept.code} in university_id={university_id}")
        return dept

    @staticmethod
    @transaction.atomic
    def update_department(department_id, data: dict, requesting_user) -> Department:
        dept = DepartmentService.get_department(department_id, requesting_user)
        for field in ['name', 'description', 'is_active']:
            if field in data:
                setattr(dept, field, data[field])
        dept.save()
        return dept

    @staticmethod
    @transaction.atomic
    def delete_department(department_id, requesting_user):
        dept = DepartmentService.get_department(department_id, requesting_user)
        dept.soft_delete()
        logger.info(f"Department soft-deleted: {dept.code}")


# ── Programme Service ─────────────────────────────────────────────────────────

class ProgrammeService:

    @staticmethod
    def get_programmes(department_id, requesting_user):
        try:
            dept = Department.objects.get(id=department_id, deleted_at__isnull=True)
        except Department.DoesNotExist:
            raise NotFound('Department not found.')
        _check_university_access(requesting_user, dept.university_id)
        return Programme.objects.filter(
            department_id=department_id,
            deleted_at__isnull=True,
        )

    @staticmethod
    def get_programme(programme_id, requesting_user):
        try:
            prog = Programme.objects.select_related(
                'department__university'
            ).prefetch_related('academic_levels__semesters').get(
                id=programme_id, deleted_at__isnull=True
            )
        except Programme.DoesNotExist:
            raise NotFound('Programme not found.')
        _check_university_access(requesting_user, prog.department.university_id)
        return prog

    @staticmethod
    @transaction.atomic
    def create_programme(department_id, data: dict, requesting_user) -> Programme:
        try:
            dept = Department.objects.get(id=department_id, deleted_at__isnull=True)
        except Department.DoesNotExist:
            raise NotFound('Department not found.')
        _check_university_access(requesting_user, dept.university_id)

        if Programme.objects.filter(
            department_id=department_id,
            code=data['code'],
            deleted_at__isnull=True,
        ).exists():
            raise ValidationError({'code': f"Programme with code '{data['code']}' already exists in this department."})

        prog = Programme.objects.create(
            department=dept,
            name=data['name'],
            code=data['code'],
            degree_type=data.get('degree_type', 'bachelor'),
            duration_years=data.get('duration_years', 4),
            total_credits=data.get('total_credits', 120),
            description=data.get('description', ''),
        )
        logger.info(f"Programme created: {prog.code} in department={dept.code}")
        return prog

    @staticmethod
    @transaction.atomic
    def update_programme(programme_id, data: dict, requesting_user) -> Programme:
        prog = ProgrammeService.get_programme(programme_id, requesting_user)
        for field in ['name', 'degree_type', 'duration_years', 'total_credits', 'description', 'is_active']:
            if field in data:
                setattr(prog, field, data[field])
        prog.save()
        return prog

    @staticmethod
    @transaction.atomic
    def delete_programme(programme_id, requesting_user):
        prog = ProgrammeService.get_programme(programme_id, requesting_user)
        prog.soft_delete()


# ── Academic Level Service ────────────────────────────────────────────────────

class AcademicLevelService:

    @staticmethod
    def get_levels(programme_id, requesting_user):
        try:
            prog = Programme.objects.select_related('department__university').get(
                id=programme_id, deleted_at__isnull=True
            )
        except Programme.DoesNotExist:
            raise NotFound('Programme not found.')
        _check_university_access(requesting_user, prog.department.university_id)
        return AcademicLevel.objects.filter(
            programme_id=programme_id,
            deleted_at__isnull=True,
        ).prefetch_related('semesters')

    @staticmethod
    def get_level(level_id, requesting_user):
        try:
            level = AcademicLevel.objects.select_related(
                'programme__department__university'
            ).prefetch_related('semesters').get(id=level_id, deleted_at__isnull=True)
        except AcademicLevel.DoesNotExist:
            raise NotFound('Academic Level not found.')
        _check_university_access(requesting_user, level.programme.department.university_id)
        return level

    @staticmethod
    @transaction.atomic
    def create_level(programme_id, data: dict, requesting_user) -> AcademicLevel:
        try:
            prog = Programme.objects.select_related('department__university').get(
                id=programme_id, deleted_at__isnull=True
            )
        except Programme.DoesNotExist:
            raise NotFound('Programme not found.')
        _check_university_access(requesting_user, prog.department.university_id)

        if AcademicLevel.objects.filter(
            programme_id=programme_id,
            level_number=data['level_number'],
            deleted_at__isnull=True,
        ).exists():
            raise ValidationError({'level_number': f"Level {data['level_number']} already exists in this programme."})

        level = AcademicLevel.objects.create(
            programme=prog,
            name=data['name'],
            level_number=data['level_number'],
            description=data.get('description', ''),
        )
        logger.info(f"Academic Level created: {level.name} in programme={prog.code}")
        return level

    @staticmethod
    @transaction.atomic
    def delete_level(level_id, requesting_user):
        level = AcademicLevelService.get_level(level_id, requesting_user)
        level.soft_delete()


# ── Semester Service ──────────────────────────────────────────────────────────

class SemesterService:

    @staticmethod
    def get_semesters(level_id, requesting_user):
        try:
            level = AcademicLevel.objects.select_related(
                'programme__department__university'
            ).get(id=level_id, deleted_at__isnull=True)
        except AcademicLevel.DoesNotExist:
            raise NotFound('Academic Level not found.')
        _check_university_access(requesting_user, level.programme.department.university_id)
        return Semester.objects.filter(academic_level_id=level_id, deleted_at__isnull=True)

    @staticmethod
    @transaction.atomic
    def create_semester(level_id, data: dict, requesting_user) -> Semester:
        try:
            level = AcademicLevel.objects.select_related(
                'programme__department__university'
            ).get(id=level_id, deleted_at__isnull=True)
        except AcademicLevel.DoesNotExist:
            raise NotFound('Academic Level not found.')
        _check_university_access(requesting_user, level.programme.department.university_id)

        if Semester.objects.filter(
            academic_level_id=level_id,
            semester_number=data['semester_number'],
            deleted_at__isnull=True,
        ).exists():
            raise ValidationError({
                'semester_number': f"Semester {data['semester_number']} already exists in this level."
            })

        # Only one current semester per level
        if data.get('is_current'):
            Semester.objects.filter(
                academic_level_id=level_id,
                is_current=True,
                deleted_at__isnull=True,
            ).update(is_current=False)

        semester = Semester.objects.create(
            academic_level=level,
            name=data['name'],
            semester_number=data['semester_number'],
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            is_current=data.get('is_current', False),
        )
        logger.info(f"Semester created: {semester.name}")
        return semester

    @staticmethod
    @transaction.atomic
    def delete_semester(semester_id, requesting_user):
        try:
            semester = Semester.objects.select_related(
                'academic_level__programme__department__university'
            ).get(id=semester_id, deleted_at__isnull=True)
        except Semester.DoesNotExist:
            raise NotFound('Semester not found.')
        _check_university_access(requesting_user, semester.academic_level.programme.department.university_id)
        semester.soft_delete()
