import uuid
from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """Returns only non-deleted records."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager):
    """Returns all records including soft-deleted."""

    def get_queryset(self):
        return super().get_queryset()


class BaseModel(models.Model):
    """
    Abstract base model for ALL models in this project.

    Provides:
    - UUID primary key
    - created_at / updated_at timestamps
    - Soft delete via deleted_at
    - Dual managers: objects (active only) and all_objects (including deleted)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """Mark record as deleted without removing from DB."""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at', 'updated_at'])

    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at', 'updated_at'])

    @property
    def is_deleted(self):
        return self.deleted_at is not None
