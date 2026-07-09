import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.roles.models import Role, RoleChoices
from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def super_admin_role(db):
    return Role.objects.create(
        name=RoleChoices.SUPER_ADMIN,
        display_name='Super Admin',
        is_active=True,
    )


@pytest.fixture
def super_admin_user(db, super_admin_role):
    user = User.objects.create_user(
        email='admin@test.com',
        password='Admin@123456',
        first_name='Super',
        last_name='Admin',
        role=super_admin_role,
        is_active=True,
        is_email_verified=True,
    )
    return user


@pytest.mark.django_db
class TestLoginAPI:

    def test_login_success(self, api_client, super_admin_user):
        url = reverse('auth-login')
        response = api_client.post(url, {
            'email': 'admin@test.com',
            'password': 'Admin@123456',
        }, format='json')

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'access' in data['data']
        assert 'refresh' in data['data']
        assert data['data']['user']['email'] == 'admin@test.com'
        assert data['data']['user']['role'] == 'super_admin'

    def test_login_wrong_password(self, api_client, super_admin_user):
        url = reverse('auth-login')
        response = api_client.post(url, {
            'email': 'admin@test.com',
            'password': 'WrongPassword',
        }, format='json')

        assert response.status_code == 401
        data = response.json()
        assert data['success'] is False

    def test_login_inactive_user(self, api_client, super_admin_user):
        super_admin_user.is_active = False
        super_admin_user.save()

        url = reverse('auth-login')
        response = api_client.post(url, {
            'email': 'admin@test.com',
            'password': 'Admin@123456',
        }, format='json')

        assert response.status_code == 403

    def test_login_missing_fields(self, api_client):
        url = reverse('auth-login')
        response = api_client.post(url, {'email': 'admin@test.com'}, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestLogoutAPI:

    def test_logout_success(self, api_client, super_admin_user):
        login_url = reverse('auth-login')
        login_res = api_client.post(login_url, {
            'email': 'admin@test.com',
            'password': 'Admin@123456',
        }, format='json')

        tokens = login_res.json()['data']
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        logout_url = reverse('auth-logout')
        response = api_client.post(logout_url, {'refresh': tokens['refresh']}, format='json')

        assert response.status_code == 200
        assert response.json()['success'] is True

    def test_logout_requires_auth(self, api_client):
        url = reverse('auth-logout')
        response = api_client.post(url, {'refresh': 'fake'}, format='json')
        assert response.status_code == 401


@pytest.mark.django_db
class TestForgotPasswordAPI:

    def test_forgot_password_always_returns_200(self, api_client):
        url = reverse('forgot-password')
        # Known email
        response = api_client.post(url, {'email': 'notexist@test.com'}, format='json')
        assert response.status_code == 200
        assert response.json()['success'] is True

    def test_forgot_password_missing_email(self, api_client):
        url = reverse('forgot-password')
        response = api_client.post(url, {}, format='json')
        assert response.status_code == 400
