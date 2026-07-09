import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class UserManager(BaseUserManager):
    """Default manager — returns only active (non-deleted) users."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class AllUsersManager(BaseUserManager):
    """Returns ALL users including soft-deleted ones."""

    def get_queryset(self):
        return super().get_queryset()


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model.
    - Email is the login identifier (not username)
    - UUID primary key
    - Role is a FK to Role model (single role per user, enforced by business rules)
    - Supports soft delete via deleted_at
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Role FK — assigned at creation, can be changed by admin
    role = models.ForeignKey(
        'roles.Role',
        on_delete=models.PROTECT,
        related_name='users',
        null=True,
        blank=True,
    )

    # Flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    # Email verification
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)

    # Password reset
    password_reset_token = models.UUIDField(null=True, blank=True)
    password_reset_sent_at = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()
    all_objects = AllUsersManager()

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active', 'deleted_at']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    @property
    def role_name(self):
        return self.role.name if self.role else None

    @property
    def is_super_admin(self):
        return self.role_name == 'super_admin'

    @property
    def is_university_admin(self):
        return self.role_name == 'university_admin'

    @property
    def is_lecturer(self):
        return self.role_name == 'lecturer'

    @property
    def is_reviewer(self):
        return self.role_name == 'reviewer'

    @property
    def is_student(self):
        return self.role_name == 'student'

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['deleted_at', 'is_active', 'updated_at'])

    def restore(self):
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=['deleted_at', 'is_active', 'updated_at'])
