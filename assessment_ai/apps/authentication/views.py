import logging

from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.utils.response import ApiResponse
from .serializers import (
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    LogoutSerializer,
)
from .services import AuthService

logger = logging.getLogger(__name__)


class LoginThrottle(AnonRateThrottle):
    scope = 'login'


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    @extend_schema(
        tags=['Authentication'],
        summary='Login',
        description='Authenticate with email and password. Returns JWT access + refresh tokens.',
        request=LoginSerializer,
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )

        if not user:
            return ApiResponse.error(
                message='Invalid email or password.',
                status_code=401,
            )

        if not user.is_active:
            return ApiResponse.error(
                message='Your account has been deactivated. Contact your administrator.',
                status_code=403,
            )

        tokens = AuthService.get_tokens_for_user(user)
        AuthService.record_login_ip(user, request)

        return ApiResponse.success(
            data={
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'full_name': user.get_full_name(),
                    'role': user.role.name if user.role else None,
                    'role_display': user.role.display_name if user.role else None,
                    'is_email_verified': user.is_email_verified,
                },
            },
            message='Login successful.',
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Authentication'],
        summary='Logout',
        description='Blacklists the refresh token. Pass the refresh token in the request body.',
        request=LogoutSerializer,
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.logout(serializer.validated_data['refresh'])
        return ApiResponse.success(message='Logged out successfully.')


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    @extend_schema(
        tags=['Authentication'],
        summary='Forgot Password',
        description='Sends a password reset email. Always returns 200 regardless of whether email exists (security).',
        request=ForgotPasswordSerializer,
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.initiate_password_reset(serializer.validated_data['email'])
        # Always return 200 — do not reveal whether email exists
        return ApiResponse.success(
            message='If this email is registered, a reset link has been sent.'
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        summary='Reset Password',
        description='Validates the reset token from email and sets a new password.',
        request=ResetPasswordSerializer,
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.reset_password(
            token=serializer.validated_data['token'],
            new_password=serializer.validated_data['new_password'],
        )
        return ApiResponse.success(message='Password reset successfully. Please log in.')


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        summary='Refresh Token',
        description='Get a new access token using a valid refresh token.',
    )
    def post(self, request):
        from rest_framework_simplejwt.views import TokenRefreshView as BaseRefreshView
        from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

        try:
            refresh_token = request.data.get('refresh')
            from rest_framework_simplejwt.tokens import RefreshToken
            token = RefreshToken(refresh_token)
            data = {
                'access': str(token.access_token),
                'refresh': str(token),
            }
            return ApiResponse.success(data=data, message='Token refreshed.')
        except Exception:
            return ApiResponse.error(
                message='Invalid or expired refresh token.',
                status_code=401,
            )
