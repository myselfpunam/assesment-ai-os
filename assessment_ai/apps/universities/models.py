from django.db import models
from django.utils.text import slugify
from core.models import BaseModel


class University(BaseModel):
    """
    Top-level tenant. Every piece of data in the system belongs to a University.
    Tenant isolation is enforced at the service layer — every query is scoped
    to the requesting user's university.
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, db_index=True)
    logo = models.ImageField(upload_to='universities/logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_universities',
    )

    class Meta:
        db_table = 'universities'
        verbose_name = 'University'
        verbose_name_plural = 'Universities'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'deleted_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while University.all_objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class UniversitySettings(BaseModel):
    """
    Per-university configuration. Auto-created when a University is created.
    Controls feature flags, limits, and defaults for each tenant.
    """
    university = models.OneToOneField(
        University,
        on_delete=models.CASCADE,
        related_name='settings',
    )

    # Capacity limits
    max_students = models.PositiveIntegerField(default=10000)
    max_lecturers = models.PositiveIntegerField(default=500)
    max_departments = models.PositiveIntegerField(default=50)

    # AI Configuration
    allow_ai_generation = models.BooleanField(default=True)
    ai_questions_per_quiz = models.PositiveIntegerField(default=20)
    ai_model_preference = models.CharField(max_length=50, default='gpt-4o')

    # Academic Settings
    allow_student_self_registration = models.BooleanField(default=False)
    academic_year_start_month = models.PositiveSmallIntegerField(
        default=9,
        help_text='Month number (1=Jan, 9=Sep)'
    )
    default_language = models.CharField(max_length=10, default='en')

    # Grading
    grading_scale = models.JSONField(
        default=dict,
        help_text='e.g. {"A": 90, "B": 80, "C": 70, "D": 60, "F": 0}'
    )

    # Quiz Settings
    allow_late_submission = models.BooleanField(default=False)
    max_quiz_attempts = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = 'university_settings'
        verbose_name = 'University Settings'
        verbose_name_plural = 'University Settings'

    def __str__(self):
        return f"Settings → {self.university.name}"


class UniversityAdmin(BaseModel):
    """
    Links a user with role=university_admin to a specific University.
    A user can be admin of multiple universities (edge case but supported).
    is_primary = True means the main point of contact for that university.
    """
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='admins',
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='university_admin_profiles',
    )
    is_primary = models.BooleanField(default=False)
    assigned_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_university_admins',
    )

    class Meta:
        db_table = 'university_admins'
        verbose_name = 'University Admin'
        verbose_name_plural = 'University Admins'
        unique_together = [['university', 'user']]
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} → {self.university.name}"
