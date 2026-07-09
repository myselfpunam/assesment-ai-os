from django.db import models
from core.models import BaseModel


class Course(BaseModel):
    """
    A subject/module offered by a Department.
    e.g. "Data Structures", "Algorithms", "Database Systems"
    """
    department = models.ForeignKey(
        'academic.Department',
        on_delete=models.CASCADE,
        related_name='courses',
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, help_text='e.g. CSE301, MATH101')
    description = models.TextField(blank=True, default='')
    credit_hours = models.PositiveSmallIntegerField(default=3)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['code']
        unique_together = [['department', 'code']]
        indexes = [
            models.Index(fields=['department', 'is_active']),
        ]

    def __str__(self):
        return f"{self.code} — {self.name}"

    @property
    def university(self):
        return self.department.university


class CourseSection(BaseModel):
    """
    A specific offering of a Course in a given Semester.
    e.g. "CSE301 - Section A" in "Semester 1"
    Multiple sections can be created for the same course in the same semester.
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='sections',
    )
    semester = models.ForeignKey(
        'academic.Semester',
        on_delete=models.CASCADE,
        related_name='sections',
    )
    section_code = models.CharField(max_length=20, help_text='e.g. A, B, SEC-01')
    max_students = models.PositiveIntegerField(default=40)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'course_sections'
        verbose_name = 'Course Section'
        verbose_name_plural = 'Course Sections'
        ordering = ['section_code']
        unique_together = [['course', 'semester', 'section_code']]

    def __str__(self):
        return f"{self.course.code} — {self.section_code} ({self.semester.name})"


class LecturerAssignment(BaseModel):
    """
    Assigns a Lecturer (User with lecturer role) to a CourseSection.
    One section can have multiple lecturers; one is marked as primary.
    """
    section = models.ForeignKey(
        CourseSection,
        on_delete=models.CASCADE,
        related_name='lecturer_assignments',
    )
    lecturer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='teaching_assignments',
    )
    is_primary = models.BooleanField(default=True)
    assigned_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='lecturer_assignments_made',
    )

    class Meta:
        db_table = 'lecturer_assignments'
        verbose_name = 'Lecturer Assignment'
        verbose_name_plural = 'Lecturer Assignments'
        unique_together = [['section', 'lecturer']]

    def __str__(self):
        return f"{self.lecturer.get_full_name()} → {self.section}"


class CourseMaterial(BaseModel):
    """
    Study material (PDF/DOCX/PPTX) uploaded by a lecturer for a section.
    Extracted text is cached so AI quiz generation doesn't re-read the file.
    """
    section = models.ForeignKey(
        CourseSection,
        on_delete=models.CASCADE,
        related_name='materials',
    )
    uploaded_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_materials',
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='course_materials/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)  # pdf, docx, pptx
    file_size_kb = models.PositiveIntegerField(default=0)
    extracted_text = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'course_materials'
        verbose_name = 'Course Material'
        verbose_name_plural = 'Course Materials'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.section})"
