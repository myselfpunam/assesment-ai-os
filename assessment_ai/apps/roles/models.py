from django.db import models
from core.models import BaseModel


class RoleChoices(models.TextChoices):
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    UNIVERSITY_ADMIN = 'university_admin', 'University Admin'
    LECTURER = 'lecturer', 'Lecturer'
    REVIEWER = 'reviewer', 'Reviewer'
    STUDENT = 'student', 'Student'


class Role(BaseModel):
    """
    System roles. Pre-seeded via migrations.
    These are NOT arbitrary—they map to specific permission scopes.
    """

    name = models.CharField(
        max_length=50,
        choices=RoleChoices.choices,
        unique=True,
    )
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']

    def __str__(self):
        return self.display_name
