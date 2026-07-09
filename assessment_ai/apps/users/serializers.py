from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from apps.roles.serializers import RoleSerializer
from apps.roles.models import Role


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lists."""
    full_name = serializers.SerializerMethodField()
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'full_name', 'role_name', 'is_active', 'created_at',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail views."""
    full_name = serializers.SerializerMethodField()
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'avatar', 'role', 'is_active',
            'is_email_verified', 'last_login_ip',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at', 'is_email_verified', 'last_login_ip']

    def get_full_name(self, obj):
        return obj.get_full_name()


class CreateUserSerializer(serializers.ModelSerializer):
    """Used by admins to create users."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    role_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone_number',
            'role_id', 'password', 'confirm_password',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})

        role_id = attrs.pop('role_id')
        try:
            role = Role.objects.get(id=role_id, is_active=True)
        except Role.DoesNotExist:
            raise serializers.ValidationError({'role_id': 'Invalid or inactive role.'})
        attrs['role'] = role
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    """Allows updating profile fields only — not email or role."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'avatar']


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({'confirm_new_password': 'Passwords do not match.'})
        return attrs


# ── Lecturer Profile ───────────────────────────────────────────────────────────

class LecturerSectionSerializer(serializers.Serializer):
    """One row in a lecturer's teaching schedule."""
    assignment_id = serializers.UUIDField(source='id')
    section_id = serializers.UUIDField(source='section.id')
    section_code = serializers.CharField(source='section.section_code')
    course_name = serializers.CharField(source='section.course.name')
    course_code = serializers.CharField(source='section.course.code')
    semester_name = serializers.CharField(source='section.semester.name')
    is_primary = serializers.BooleanField()
    student_count = serializers.SerializerMethodField()
    assessment_count = serializers.SerializerMethodField()
    material_count = serializers.SerializerMethodField()

    def get_student_count(self, obj):
        return obj.section.enrollments.filter(deleted_at__isnull=True).count()

    def get_assessment_count(self, obj):
        return obj.section.assessments.filter(deleted_at__isnull=True).count()

    def get_material_count(self, obj):
        return obj.section.materials.filter(deleted_at__isnull=True).count()


class LecturerProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_name = serializers.CharField(source='role.name', read_only=True)
    teaching_sections = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'phone_number', 'avatar',
            'role_name', 'is_active', 'teaching_sections', 'total_students',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_teaching_sections(self, obj):
        assignments = obj.teaching_assignments.filter(
            deleted_at__isnull=True
        ).select_related(
            'section__course', 'section__semester'
        ).prefetch_related(
            'section__enrollments', 'section__assessments', 'section__materials'
        )
        return LecturerSectionSerializer(assignments, many=True).data

    def get_total_students(self, obj):
        from apps.courses.models import CourseSection
        section_ids = obj.teaching_assignments.filter(
            deleted_at__isnull=True
        ).values_list('section_id', flat=True)
        from apps.students.models import Enrollment
        return Enrollment.objects.filter(
            section_id__in=section_ids,
            deleted_at__isnull=True,
        ).values('student_id').distinct().count()
