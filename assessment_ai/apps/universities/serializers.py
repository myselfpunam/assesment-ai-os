from rest_framework import serializers
from .models import University, UniversitySettings, UniversityAdmin
from apps.users.serializers import UserListSerializer


class UniversitySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversitySettings
        fields = [
            'id', 'max_students', 'max_lecturers', 'max_departments',
            'allow_ai_generation', 'ai_questions_per_quiz', 'ai_model_preference',
            'allow_student_self_registration', 'academic_year_start_month',
            'default_language', 'grading_scale',
            'allow_late_submission', 'max_quiz_attempts',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UniversityListSerializer(serializers.ModelSerializer):
    """Lightweight — used in list views."""
    admin_count = serializers.SerializerMethodField()

    class Meta:
        model = University
        fields = [
            'id', 'name', 'slug', 'logo', 'email',
            'city', 'country', 'is_active', 'admin_count', 'created_at',
        ]

    def get_admin_count(self, obj):
        return obj.admins.filter(deleted_at__isnull=True).count()


class UniversityDetailSerializer(serializers.ModelSerializer):
    """Full detail — used in retrieve views."""
    settings = UniversitySettingsSerializer(read_only=True)
    created_by = UserListSerializer(read_only=True)

    class Meta:
        model = University
        fields = [
            'id', 'name', 'slug', 'logo', 'website', 'email', 'phone',
            'address', 'city', 'country', 'timezone', 'is_active',
            'settings', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'created_by']


class CreateUniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = [
            'name', 'logo', 'website', 'email', 'phone',
            'address', 'city', 'country', 'timezone',
        ]

    def validate_name(self, value):
        if University.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError('A university with this name already exists.')
        return value


class UpdateUniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = [
            'logo', 'website', 'email', 'phone',
            'address', 'city', 'country', 'timezone', 'is_active',
        ]


class UniversityAdminSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)

    class Meta:
        model = UniversityAdmin
        fields = [
            'id', 'university_name', 'user',
            'is_primary', 'assigned_by', 'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'assigned_by']


class AssignAdminSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    is_primary = serializers.BooleanField(default=False)
