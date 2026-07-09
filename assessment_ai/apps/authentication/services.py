import uuid
import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.exceptions import ValidationError, NotFound, AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)
User = get_user_model()


class AuthService:
    """
    Handles all authentication business logic.
    JWT issuance, logout (blacklist), password reset flow.
    """

    # How long a password reset link is valid
    PASSWORD_RESET_EXPIRY_HOURS = 2

    @staticmethod
    def get_tokens_for_user(user) -> dict:
        """Generate access + refresh token pair for a user."""
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['role'] = user.role.name if user.role else None
        refresh['full_name'] = user.get_full_name()

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

    @staticmethod
    def logout(refresh_token: str):
        """Blacklist the refresh token so it cannot be used again."""
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            # Already blacklisted or invalid — still return success
            logger.warning("Attempted to blacklist an already-invalid token.")

    @staticmethod
    def initiate_password_reset(email: str):
        """
        Generate a password reset token and send email.
        Always returns success (don't reveal if email exists — security best practice).
        """
        try:
            user = User.objects.get(email=email, deleted_at__isnull=True)
        except User.DoesNotExist:
            # Security: do not reveal whether the email exists
            logger.info(f"Password reset requested for unknown email: {email}")
            return

        reset_token = uuid.uuid4()
        user.password_reset_token = reset_token
        user.password_reset_sent_at = timezone.now()
        user.save(update_fields=['password_reset_token', 'password_reset_sent_at', 'updated_at'])

        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

        try:
            send_mail(
                subject='Reset your Assessment AI password',
                message=f'Click the link to reset your password: {reset_link}\n\nThis link expires in 2 hours.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"Password reset email sent to {email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")

    @staticmethod
    def reset_password(token: uuid.UUID, new_password: str):
        """Validate the reset token and set the new password."""
        try:
            user = User.objects.get(
                password_reset_token=token,
                deleted_at__isnull=True,
            )
        except User.DoesNotExist:
            raise ValidationError({'token': 'Invalid or expired reset token.'})

        expiry_cutoff = timezone.now() - timedelta(hours=AuthService.PASSWORD_RESET_EXPIRY_HOURS)
        if user.password_reset_sent_at < expiry_cutoff:
            raise ValidationError({'token': 'This reset link has expired. Please request a new one.'})

        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_sent_at = None
        user.save(update_fields=['password', 'password_reset_token', 'password_reset_sent_at', 'updated_at'])
        logger.info(f"Password successfully reset for user: {user.email}")

    @staticmethod
    def record_login_ip(user, request):
        """Record the IP address of the last login."""
        ip = AuthService._get_client_ip(request)
        if ip:
            user.last_login_ip = ip
            user.save(update_fields=['last_login_ip', 'updated_at'])

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
