from rest_framework import serializers
from .models import Batch, StudentProfile, Enrollment, EnrollmentStatus


# ── Batch ─────────────────────────────────────────────────────────────────────

class BatchSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(source='programme.name', read_only=True)
    programme_code = serializers.CharField(source='programme.code', read_only=True)
    academic_level_name = serializers.CharField(source='academic_level.name', read_only=True)
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = ['id', 'name', 'programme_name', 'programme_code',
                  'academic_level_name', 'year', 'student_count', 'is_active', 'created_at']

    def get_student_count(self, obj):
        return obj.students.count()


class CreateBatchSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    programme_id = serializers.UUIDField()
    academic_level_id = serializers.UUIDField(required=False, allow_null=True)
    year = serializers.IntegerField(min_value=2000, max_value=2100)


class UpdateBatchSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    academic_level_id = serializers.UUIDField(required=False, allow_null=True)
    year = serializers.IntegerField(min_value=2000, max_value=2100, required=False)
    is_active = serializers.BooleanField(required=False)


# ── Student Profile ───────────────────────────────────────────────────────────

class StudentProfileListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    programme_name = serializers.CharField(source='programme.name', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)

    class Meta:
        model = StudentProfile
        fields = ['id', 'student_id', 'full_name', 'email',
                  'programme_name', 'batch_name', 'enrollment_year', 'is_active', 'created_at']


class StudentProfileDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    programme_name = serializers.CharField(source='programme.name', read_only=True)
    programme_code = serializers.CharField(source='programme.code', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    enrollment_count = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = ['id', 'student_id', 'full_name', 'email', 'phone_number',
                  'programme_name', 'programme_code', 'batch_name',
                  'enrollment_year', 'is_active', 'enrollment_count', 'created_at', 'updated_at']

    def get_enrollment_count(self, obj):
        return obj.enrollments.count()


class CreateStudentProfileSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    student_id = serializers.CharField(max_length=50)
    programme_id = serializers.UUIDField()
    batch_id = serializers.UUIDField(required=False, allow_null=True)
    enrollment_year = serializers.IntegerField(min_value=2000, max_value=2100, default=2026)


# ── Enrollment ────────────────────────────────────────────────────────────────

class EnrollmentSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    section_code = serializers.CharField(source='section.section_code', read_only=True)
    course_name = serializers.CharField(source='section.course.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student_id', 'student_name', 'course_name',
                  'section_code', 'status', 'status_display', 'grade', 'created_at']


class CreateEnrollmentSerializer(serializers.Serializer):
    student_profile_id = serializers.UUIDField()
    section_id = serializers.UUIDField()


class UpdateEnrollmentSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=EnrollmentStatus.choices, required=False)
    grade = serializers.DecimalField(max_digits=5, decimal_places=2,
                                     min_value=0, max_value=100, required=False, allow_null=True)
