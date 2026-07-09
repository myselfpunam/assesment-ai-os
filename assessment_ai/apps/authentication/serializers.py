from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends default JWT serializer to include user info in token response.
    Also enforces account status checks.
    """

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        if not user.is_active:
            raise serializers.ValidationError({'detail': 'Your account has been deactivated.'})

        if user.deleted_at is not None:
            raise serializers.ValidationError({'detail': 'This account no longer exists.'})

        # Resolve university for university_admin users
        university_id = None
        university_name = None
        if user.is_university_admin:
            from apps.universities.services import UniversityService
            university = UniversityService.get_university_for_user(user)
            if university:
                university_id = str(university.id)
                university_name = university.name

        data['user'] = {
            'id': str(user.id),
            'email': user.email,
            'full_name': user.get_full_name(),
            'role': user.role.name if user.role else None,
            'role_display': user.role.display_name if user.role else None,
            'is_email_verified': user.is_email_verified,
            'university_id': university_id,
            'university_name': university_name,
        }
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role.name if user.role else None
        token['full_name'] = user.get_full_name()

        # Embed university_id in JWT for tenant isolation
        if user.is_university_admin:
            from apps.universities.services import UniversityService
            university = UniversityService.get_university_for_user(user)
            token['university_id'] = str(university.id) if university else None
        else:
            token['university_id'] = None

        return token


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
