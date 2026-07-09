import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.roles.models import Role, RoleChoices
from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def roles(db):
    super_admin = Role.objects.create(name=RoleChoices.SUPER_ADMIN, display_name='Super Admin', is_active=True)
    lecturer = Role.objects.create(name=RoleChoices.LECTURER, display_name='Lecturer', is_active=True)
    student = Role.objects.create(name=RoleChoices.STUDENT, display_name='Student', is_active=True)
    return {'super_admin': super_admin, 'lecturer': lecturer, 'student': student}


@pytest.fixture
def super_admin(db, roles):
    user = User.objects.create_user(
        email='admin@test.com',
        password='Admin@123456',
        first_name='Super',
        last_name='Admin',
        role=roles['super_admin'],
        is_active=True,
    )
    return user


@pytest.fixture
def authenticated_admin(api_client, super_admin):
    login_url = reverse('auth-login')
    res = api_client.post(login_url, {
        'email': 'admin@test.com',
        'password': 'Admin@123456',
    }, format='json')
    token = res.json()['data']['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.mark.django_db
class TestUserCreateAPI:

    def test_create_lecturer_as_super_admin(self, authenticated_admin, roles):
        url = reverse('user-list-create')
        response = authenticated_admin.post(url, {
            'email': 'lecturer@test.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role_id': str(roles['lecturer'].id),
            'password': 'Lecturer@123456',
            'confirm_password': 'Lecturer@123456',
        }, format='json')

        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert data['data']['email'] == 'lecturer@test.com'

    def test_create_user_password_mismatch(self, authenticated_admin, roles):
        url = reverse('user-list-create')
        response = authenticated_admin.post(url, {
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role_id': str(roles['student'].id),
            'password': 'Password@123',
            'confirm_password': 'DifferentPassword@123',
        }, format='json')
        assert response.status_code == 400

    def test_create_user_duplicate_email(self, authenticated_admin, roles, super_admin):
        url = reverse('user-list-create')
        response = authenticated_admin.post(url, {
            'email': 'admin@test.com',  # Already exists
            'first_name': 'Dup',
            'last_name': 'User',
            'role_id': str(roles['student'].id),
            'password': 'Password@123',
            'confirm_password': 'Password@123',
        }, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestMeAPI:

    def test_get_own_profile(self, authenticated_admin, super_admin):
        url = reverse('user-me')
        response = authenticated_admin.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data['data']['email'] == super_admin.email

    def test_update_own_profile(self, authenticated_admin):
        url = reverse('user-me')
        response = authenticated_admin.patch(url, {
            'first_name': 'Updated',
        }, format='json')
        assert response.status_code == 200
        assert response.json()['data']['first_name'] == 'Updated'
