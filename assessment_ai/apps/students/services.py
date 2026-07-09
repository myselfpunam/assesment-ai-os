from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404

from apps.academic.models import Programme, AcademicLevel
from apps.courses.models import CourseSection
from apps.users.models import User
from .models import Batch, StudentProfile, Enrollment


class BatchService:

    @staticmethod
    def get_batches(user, programme_id=None):
        qs = Batch.objects.select_related('programme', 'academic_level')
        if programme_id:
            qs = qs.filter(programme_id=programme_id)
        return qs

    @staticmethod
    def create_batch(data, requesting_user):
        programme = get_object_or_404(Programme, id=data['programme_id'])
        academic_level = None
        if data.get('academic_level_id'):
            academic_level = get_object_or_404(AcademicLevel, id=data['academic_level_id'])

        if Batch.objects.filter(programme=programme, name=data['name'], year=data['year']).exists():
            raise ValidationError({'name': [f"Batch '{data['name']}' already exists for this programme in {data['year']}."]})

        return Batch.objects.create(
            name=data['name'],
            programme=programme,
            academic_level=academic_level,
            year=data['year'],
        )

    @staticmethod
    def get_batch(batch_id, user):
        return get_object_or_404(Batch, id=batch_id)

    @staticmethod
    def update_batch(batch_id, data, user):
        batch = get_object_or_404(Batch, id=batch_id)
        if 'academic_level_id' in data:
            if data['academic_level_id']:
                batch.academic_level = get_object_or_404(AcademicLevel, id=data['academic_level_id'])
            else:
                batch.academic_level = None
            data.pop('academic_level_id')
        for key, value in data.items():
            setattr(batch, key, value)
        batch.save()
        return batch

    @staticmethod
    def delete_batch(batch_id, user):
        batch = get_object_or_404(Batch, id=batch_id)
        batch.soft_delete()


class StudentService:

    @staticmethod
    def get_students(user, programme_id=None, batch_id=None):
        qs = StudentProfile.objects.select_related(
            'user', 'programme', 'batch'
        )
        if programme_id:
            qs = qs.filter(programme_id=programme_id)
        if batch_id:
            qs = qs.filter(batch_id=batch_id)
        return qs

    @staticmethod
    def create_student(data, requesting_user):
        user = get_object_or_404(User, id=data['user_id'])

        if not user.is_student:
            raise ValidationError({'user_id': ['User does not have the student role.']})

        if StudentProfile.objects.filter(user=user).exists():
            raise ValidationError({'user_id': ['Student profile already exists for this user.']})

        if StudentProfile.objects.filter(student_id=data['student_id']).exists():
            raise ValidationError({'student_id': [f"Student ID '{data['student_id']}' is already taken."]})

        programme = get_object_or_404(Programme, id=data['programme_id'])
        batch = None
        if data.get('batch_id'):
            batch = get_object_or_404(Batch, id=data['batch_id'])

        return StudentProfile.objects.create(
            user=user,
            student_id=data['student_id'],
            programme=programme,
            batch=batch,
            enrollment_year=data.get('enrollment_year', 2026),
        )

    @staticmethod
    def get_student(student_id, user):
        return get_object_or_404(
            StudentProfile.objects.select_related('user', 'programme', 'batch'),
            id=student_id
        )

    @staticmethod
    def update_student(student_id, data, user):
        student = get_object_or_404(StudentProfile, id=student_id)
        if 'batch_id' in data:
            if data['batch_id']:
                student.batch = get_object_or_404(Batch, id=data['batch_id'])
            else:
                student.batch = None
            data.pop('batch_id')
        for key, value in data.items():
            setattr(student, key, value)
        student.save()
        return student


class EnrollmentService:

    @staticmethod
    def get_enrollments(section_id=None, student_id=None):
        qs = Enrollment.objects.select_related(
            'student__user', 'section__course', 'section__semester'
        )
        if section_id:
            qs = qs.filter(section_id=section_id)
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs

    @staticmethod
    def enroll_student(data, requesting_user):
        student = get_object_or_404(StudentProfile, id=data['student_profile_id'])
        section = get_object_or_404(CourseSection, id=data['section_id'])

        if Enrollment.objects.filter(student=student, section=section).exists():
            raise ValidationError({'student_profile_id': ['Student is already enrolled in this section.']})

        enrolled_count = Enrollment.objects.filter(
            section=section, status='enrolled'
        ).count()
        if enrolled_count >= section.max_students:
            raise ValidationError({'section_id': [f'Section is full. Maximum {section.max_students} students allowed.']})

        return Enrollment.objects.create(
            student=student,
            section=section,
            enrolled_by=requesting_user,
        )

    @staticmethod
    def update_enrollment(enrollment_id, data, user):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        for key, value in data.items():
            setattr(enrollment, key, value)
        enrollment.save()
        return enrollment

    @staticmethod
    def drop_enrollment(enrollment_id, user):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        enrollment.status = 'dropped'
        enrollment.save(update_fields=['status', 'updated_at'])
        return enrollment
