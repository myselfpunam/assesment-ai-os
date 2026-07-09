from django.db import models
from core.models import BaseModel


class Batch(BaseModel):
    """
    A cohort/group of students in a Programme.
    e.g. "CSE Batch 2024", "BBA Batch 2023"
    """
    name = models.CharField(max_length=100)
    programme = models.ForeignKey(
        'academic.Programme',
        on_delete=models.CASCADE,
        related_name='batches',
    )
    academic_level = models.ForeignKey(
        'academic.AcademicLevel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='batches',
    )
    year = models.PositiveIntegerField(help_text='Intake year e.g. 2024')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'batches'
        verbose_name = 'Batch'
        verbose_name_plural = 'Batches'
        ordering = ['-year', 'name']
        unique_together = [['programme', 'name', 'year']]

    def __str__(self):
        return f"{self.name} ({self.year})"


class StudentProfile(BaseModel):
    """
    Extra profile for users with student role.
    Created when a student is registered in the system.
    """
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='student_profile',
    )
    student_id = models.CharField(
        max_length=50,
        unique=True,
        help_text='e.g. CSE-2024-001',
    )
    programme = models.ForeignKey(
        'academic.Programme',
        on_delete=models.PROTECT,
        related_name='students',
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
    )
    enrollment_year = models.PositiveIntegerField(default=2026)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        ordering = ['student_id']

    def __str__(self):
        return f"{self.student_id} — {self.user.get_full_name()}"

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email


class EnrollmentStatus(models.TextChoices):
    ENROLLED = 'enrolled', 'Enrolled'
    DROPPED = 'dropped', 'Dropped'
    COMPLETED = 'completed', 'Completed'


class Enrollment(BaseModel):
    """
    A student enrolled in a specific CourseSection.
    Tracks status and final grade.
    """
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    section = models.ForeignKey(
        'courses.CourseSection',
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.ENROLLED,
    )
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Final grade (0–100)',
    )
    enrolled_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='enrollments_made',
    )

    class Meta:
        db_table = 'enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        ordering = ['-created_at']
        unique_together = [['student', 'section']]

    def __str__(self):
        return f"{self.student.student_id} → {self.section}"
