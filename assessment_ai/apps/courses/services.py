from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404

from apps.academic.models import Department, Semester
from apps.users.models import User
from .models import Course, CourseSection, LecturerAssignment, CourseMaterial


def _check_department_access(department, user):
    if user.is_super_admin:
        return
    if user.is_university_admin:
        from apps.universities.models import UniversityAdmin
        has_access = UniversityAdmin.objects.filter(
            user=user,
            university=department.university
        ).exists()
        if not has_access:
            raise PermissionDenied("You do not have access to this department's university.")
    elif not user.is_lecturer:
        raise PermissionDenied("Insufficient permissions.")


class CourseService:

    @staticmethod
    def get_courses(department_id, user):
        dept = get_object_or_404(Department, id=department_id)
        return Course.objects.filter(department=dept).select_related('department__university')

    @staticmethod
    def create_course(department_id, data, requesting_user):
        dept = get_object_or_404(Department, id=department_id)
        _check_department_access(dept, requesting_user)

        if Course.objects.filter(department=dept, code=data['code']).exists():
            raise ValidationError({'code': [f"Course code '{data['code']}' already exists in this department."]})

        return Course.objects.create(department=dept, **data)

    @staticmethod
    def get_course(course_id, user):
        return get_object_or_404(Course, id=course_id)

    @staticmethod
    def update_course(course_id, data, user):
        course = get_object_or_404(Course, id=course_id)
        _check_department_access(course.department, user)
        for key, value in data.items():
            setattr(course, key, value)
        course.save()
        return course

    @staticmethod
    def delete_course(course_id, user):
        course = get_object_or_404(Course, id=course_id)
        _check_department_access(course.department, user)
        course.soft_delete()


class CourseSectionService:

    @staticmethod
    def get_sections(course_id, user):
        course = get_object_or_404(Course, id=course_id)
        return CourseSection.objects.filter(course=course).select_related(
            'course', 'semester'
        ).prefetch_related('lecturer_assignments__lecturer')

    @staticmethod
    def create_section(course_id, data, requesting_user):
        course = get_object_or_404(Course, id=course_id)
        _check_department_access(course.department, requesting_user)

        semester_id = data.pop('semester_id')
        semester = get_object_or_404(Semester, id=semester_id)

        if CourseSection.objects.filter(
            course=course,
            semester=semester,
            section_code=data['section_code']
        ).exists():
            raise ValidationError({
                'section_code': [f"Section '{data['section_code']}' already exists for this course in this semester."]
            })

        return CourseSection.objects.create(course=course, semester=semester, **data)

    @staticmethod
    def get_section(section_id, user):
        return get_object_or_404(
            CourseSection.objects.select_related('course', 'semester').prefetch_related(
                'lecturer_assignments__lecturer'
            ),
            id=section_id
        )

    @staticmethod
    def update_section(section_id, data, user):
        section = get_object_or_404(CourseSection, id=section_id)
        _check_department_access(section.course.department, user)
        for key, value in data.items():
            setattr(section, key, value)
        section.save()
        return section

    @staticmethod
    def delete_section(section_id, user):
        section = get_object_or_404(CourseSection, id=section_id)
        _check_department_access(section.course.department, user)
        section.soft_delete()

    @staticmethod
    def assign_lecturer(section_id, lecturer_id, requesting_user):
        section = get_object_or_404(CourseSection, id=section_id)
        _check_department_access(section.course.department, requesting_user)

        lecturer = get_object_or_404(User, id=lecturer_id)

        if not lecturer.is_lecturer:
            raise ValidationError({'lecturer_id': ['User does not have the lecturer role.']})

        if LecturerAssignment.objects.filter(section=section, lecturer=lecturer).exists():
            raise ValidationError({'lecturer_id': ['Lecturer is already assigned to this section.']})

        is_primary = not LecturerAssignment.objects.filter(section=section).exists()

        return LecturerAssignment.objects.create(
            section=section,
            lecturer=lecturer,
            is_primary=is_primary,
            assigned_by=requesting_user,
        )

    @staticmethod
    def remove_lecturer(section_id, lecturer_id, requesting_user):
        section = get_object_or_404(CourseSection, id=section_id)
        _check_department_access(section.course.department, requesting_user)
        assignment = get_object_or_404(LecturerAssignment, section=section, lecturer_id=lecturer_id)
        assignment.delete()


class CourseMaterialService:

    ALLOWED_EXTENSIONS = ['pdf', 'docx', 'pptx']

    @staticmethod
    def upload_material(section_id, user, title, file):
        from apps.assessments.document_extractor import extract_text

        section = get_object_or_404(CourseSection, id=section_id, deleted_at__isnull=True)

        filename = file.name.lower()
        ext = filename.rsplit('.', 1)[-1] if '.' in filename else ''
        if ext not in CourseMaterialService.ALLOWED_EXTENSIONS:
            raise ValueError(f'Invalid file type ".{ext}". Only PDF, DOCX, PPTX allowed.')

        file_bytes = file.read()
        file_size_kb = len(file_bytes) // 1024

        extracted_text = extract_text(file_bytes, file.name)

        material = CourseMaterial.objects.create(
            section=section,
            uploaded_by=user,
            title=title,
            file=file,
            original_filename=file.name,
            file_type=ext,
            file_size_kb=file_size_kb,
            extracted_text=extracted_text,
        )
        return material

    @staticmethod
    def get_materials(section_id):
        return CourseMaterial.objects.filter(
            section_id=section_id,
            is_active=True,
            deleted_at__isnull=True,
        ).select_related('uploaded_by')

    @staticmethod
    def get_material(material_id):
        return get_object_or_404(
            CourseMaterial, id=material_id, deleted_at__isnull=True
        )

    @staticmethod
    def delete_material(material_id):
        from django.utils import timezone
        material = get_object_or_404(CourseMaterial, id=material_id, deleted_at__isnull=True)
        material.deleted_at = timezone.now()
        material.save(update_fields=['deleted_at'])
