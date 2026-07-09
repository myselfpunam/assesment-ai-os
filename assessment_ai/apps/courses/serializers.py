from rest_framework import serializers
from .models import Course, CourseSection, LecturerAssignment, CourseMaterial


class CourseListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'department_name', 'department_code', 'name', 'code',
                  'credit_hours', 'is_active', 'created_at']


class CourseDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    university_name = serializers.CharField(source='department.university.name', read_only=True)
    section_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'university_name', 'department_name', 'department_code',
                  'name', 'code', 'description', 'credit_hours', 'is_active',
                  'section_count', 'created_at', 'updated_at']

    def get_section_count(self, obj):
        return obj.sections.count()


class CreateCourseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    code = serializers.CharField(max_length=20)
    description = serializers.CharField(required=False, default='', allow_blank=True)
    credit_hours = serializers.IntegerField(min_value=1, max_value=10, default=3)


class UpdateCourseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, required=False)
    code = serializers.CharField(max_length=20, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    credit_hours = serializers.IntegerField(min_value=1, max_value=10, required=False)
    is_active = serializers.BooleanField(required=False)


# ── Lecturer Assignment ────────────────────────────────────────────────────────

class LecturerAssignmentSerializer(serializers.ModelSerializer):
    lecturer_id = serializers.UUIDField(source='lecturer.id', read_only=True)
    lecturer_name = serializers.SerializerMethodField()
    lecturer_email = serializers.CharField(source='lecturer.email', read_only=True)

    class Meta:
        model = LecturerAssignment
        fields = ['id', 'lecturer_id', 'lecturer_name', 'lecturer_email',
                  'is_primary', 'created_at']

    def get_lecturer_name(self, obj):
        return obj.lecturer.get_full_name()


# ── Course Sections ────────────────────────────────────────────────────────────

class CourseSectionListSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    lecturer_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseSection
        fields = ['id', 'course_name', 'course_code', 'semester_name',
                  'section_code', 'max_students', 'is_active', 'lecturer_count', 'created_at']

    def get_lecturer_count(self, obj):
        return obj.lecturer_assignments.count()


class CourseSectionDetailSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    lecturers = LecturerAssignmentSerializer(source='lecturer_assignments', many=True, read_only=True)

    class Meta:
        model = CourseSection
        fields = ['id', 'course_name', 'course_code', 'semester_name',
                  'section_code', 'max_students', 'is_active',
                  'lecturers', 'created_at', 'updated_at']


class CreateCourseSectionSerializer(serializers.Serializer):
    semester_id = serializers.UUIDField()
    section_code = serializers.CharField(max_length=20)
    max_students = serializers.IntegerField(min_value=1, default=40)


class UpdateCourseSectionSerializer(serializers.Serializer):
    section_code = serializers.CharField(max_length=20, required=False)
    max_students = serializers.IntegerField(min_value=1, required=False)
    is_active = serializers.BooleanField(required=False)


class AssignLecturerSerializer(serializers.Serializer):
    lecturer_id = serializers.UUIDField()


# ── Course Materials ───────────────────────────────────────────────────────────

class CourseMaterialSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = CourseMaterial
        fields = [
            'id', 'title', 'original_filename', 'file_type',
            'file_size_kb', 'uploaded_by_name', 'is_active', 'created_at',
        ]

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name() if obj.uploaded_by else ''


class CourseMaterialUploadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    file = serializers.FileField()
