from django.db import models
from core.models import BaseModel


class DegreeType(models.TextChoices):
    BACHELOR = 'bachelor', 'Bachelor'
    MASTER = 'master', 'Master'
    PHD = 'phd', 'PhD'
    DIPLOMA = 'diploma', 'Diploma'
    CERTIFICATE = 'certificate', 'Certificate'


class Department(BaseModel):
    """
    Belongs to a University.
    University Admin manages departments for their own university only.
    """
    university = models.ForeignKey(
        'universities.University',
        on_delete=models.CASCADE,
        related_name='departments',
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, help_text='e.g. CSE, EEE, BBA')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']
        unique_together = [['university', 'code']]
        indexes = [
            models.Index(fields=['university', 'is_active']),
        ]

    def __str__(self):
        return f"{self.code} — {self.name}"


class Programme(BaseModel):
    """
    Belongs to a Department.
    e.g. BSc in Computer Science, MSc in Information Technology
    """
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='programmes',
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, help_text='e.g. BSC-CSE, MSC-IT')
    degree_type = models.CharField(
        max_length=20,
        choices=DegreeType.choices,
        default=DegreeType.BACHELOR,
    )
    duration_years = models.PositiveSmallIntegerField(default=4)
    total_credits = models.PositiveSmallIntegerField(default=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'programmes'
        verbose_name = 'Programme'
        verbose_name_plural = 'Programmes'
        ordering = ['name']
        unique_together = [['department', 'code']]
        indexes = [
            models.Index(fields=['department', 'is_active']),
        ]

    def __str__(self):
        return f"{self.code} — {self.name}"

    @property
    def university(self):
        return self.department.university


class AcademicLevel(BaseModel):
    """
    Belongs to a Programme.
    Represents Year 1, Year 2, Level 3 etc.
    level_number is used for ordering (1, 2, 3, 4).
    """
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='academic_levels',
    )
    name = models.CharField(max_length=100, help_text='e.g. Year 1, Level 1')
    level_number = models.PositiveSmallIntegerField(help_text='1, 2, 3...')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'academic_levels'
        verbose_name = 'Academic Level'
        verbose_name_plural = 'Academic Levels'
        ordering = ['level_number']
        unique_together = [['programme', 'level_number']]

    def __str__(self):
        return f"{self.programme.code} — {self.name}"

    @property
    def university(self):
        return self.programme.department.university


class Semester(BaseModel):
    """
    Belongs to an AcademicLevel.
    Represents Semester 1, Semester 2 within a Year/Level.
    Only one semester per academic_level can be current at a time.
    """
    academic_level = models.ForeignKey(
        AcademicLevel,
        on_delete=models.CASCADE,
        related_name='semesters',
    )
    name = models.CharField(max_length=100, help_text='e.g. Semester 1, Fall 2024')
    semester_number = models.PositiveSmallIntegerField(help_text='1, 2, 3...')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        db_table = 'semesters'
        verbose_name = 'Semester'
        verbose_name_plural = 'Semesters'
        ordering = ['semester_number']
        unique_together = [['academic_level', 'semester_number']]
        indexes = [
            models.Index(fields=['is_current', 'is_active']),
        ]

    def __str__(self):
        return f"{self.academic_level} — {self.name}"

    @property
    def university(self):
        return self.academic_level.programme.department.university
