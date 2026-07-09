from rest_framework import serializers
from .models import Department, Programme, AcademicLevel, Semester


# ── Semester ──────────────────────────────────────────────────────────────────

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = [
            'id', 'name', 'semester_number', 'start_date', 'end_date',
            'is_active', 'is_current', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        start = attrs.get('start_date')
        end = attrs.get('end_date')
        if start and end and end <= start:
            raise serializers.ValidationError({'end_date': 'End date must be after start date.'})
        return attrs


class CreateSemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['name', 'semester_number', 'start_date', 'end_date', 'is_current']

    def validate(self, attrs):
        start = attrs.get('start_date')
        end = attrs.get('end_date')
        if start and end and end <= start:
            raise serializers.ValidationError({'end_date': 'End date must be after start date.'})
        return attrs


# ── Academic Level ────────────────────────────────────────────────────────────

class AcademicLevelSerializer(serializers.ModelSerializer):
    semesters = SemesterSerializer(many=True, read_only=True)

    class Meta:
        model = AcademicLevel
        fields = [
            'id', 'name', 'level_number', 'description',
            'is_active', 'semesters', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AcademicLevelListSerializer(serializers.ModelSerializer):
    semester_count = serializers.SerializerMethodField()

    class Meta:
        model = AcademicLevel
        fields = ['id', 'name', 'level_number', 'is_active', 'semester_count']

    def get_semester_count(self, obj):
        return obj.semesters.filter(deleted_at__isnull=True).count()


class CreateAcademicLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicLevel
        fields = ['name', 'level_number', 'description']


# ── Programme ─────────────────────────────────────────────────────────────────

class ProgrammeListSerializer(serializers.ModelSerializer):
    degree_type_display = serializers.CharField(source='get_degree_type_display', read_only=True)
    level_count = serializers.SerializerMethodField()

    class Meta:
        model = Programme
        fields = [
            'id', 'name', 'code', 'degree_type', 'degree_type_display',
            'duration_years', 'total_credits', 'is_active', 'level_count',
        ]

    def get_level_count(self, obj):
        return obj.academic_levels.filter(deleted_at__isnull=True).count()


class ProgrammeDetailSerializer(serializers.ModelSerializer):
    degree_type_display = serializers.CharField(source='get_degree_type_display', read_only=True)
    academic_levels = AcademicLevelListSerializer(many=True, read_only=True)

    class Meta:
        model = Programme
        fields = [
            'id', 'name', 'code', 'degree_type', 'degree_type_display',
            'duration_years', 'total_credits', 'description',
            'is_active', 'academic_levels', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateProgrammeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programme
        fields = ['name', 'code', 'degree_type', 'duration_years', 'total_credits', 'description']

    def validate_code(self, value):
        return value.upper().strip()


# ── Department ────────────────────────────────────────────────────────────────

class DepartmentListSerializer(serializers.ModelSerializer):
    programme_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'is_active', 'programme_count', 'created_at']

    def get_programme_count(self, obj):
        return obj.programmes.filter(deleted_at__isnull=True).count()


class DepartmentDetailSerializer(serializers.ModelSerializer):
    programmes = ProgrammeListSerializer(many=True, read_only=True)
    university_name = serializers.CharField(source='university.name', read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'university_name', 'name', 'code', 'description',
            'is_active', 'programmes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description']

    def validate_code(self, value):
        return value.upper().strip()


class UpdateDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'description', 'is_active']
