import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.roles.models import Role, RoleChoices
from apps.users.models import User
from apps.universities.models import University, UniversityAdmin


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def roles(db):
    return {
        'super_admin': Role.objects.create(name=RoleChoices.SUPER_ADMIN, display_name='Super Admin', is_active=True),
        'university_admin': Role.objects.create(name=RoleChoices.UNIVERSITY_ADMIN, display_name='University Admin', is_active=True),
        'lecturer': Role.objects.create(name=RoleChoices.LECTURER, display_name='Lecturer', is_active=True),
    }


@pytest.fixture
def super_admin(db, roles):
    return User.objects.create_user(
        email='superadmin@test.com', password='Admin@123456',
        first_name='Super', last_name='Admin',
        role=roles['super_admin'], is_active=True,
    )


@pytest.fixture
def university_admin_user(db, roles):
    return User.objects.create_user(
        email='uniadmin@test.com', password='Admin@123456',
        first_name='Uni', last_name='Admin',
        role=roles['university_admin'], is_active=True,
    )


@pytest.fixture
def auth_super_admin(api_client, super_admin):
    res = api_client.post(reverse('auth-login'), {
        'email': 'superadmin@test.com', 'password': 'Admin@123456',
    }, format='json')
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.json()['data']['access']}")
    return api_client


@pytest.fixture
def sample_university(db, super_admin):
    from apps.universities.services import UniversityService
    return UniversityService.create_university(
        data={'name': 'Test University', 'city': 'Dhaka', 'country': 'Bangladesh'},
        requesting_user=super_admin,
    )


@pytest.mark.django_db
class TestUniversityCreate:

    def test_super_admin_can_create_university(self, auth_super_admin):
        url = reverse('university-list-create')
        response = auth_super_admin.post(url, {
            'name': 'BUET',
            'city': 'Dhaka',
            'country': 'Bangladesh',
            'email': 'info@buet.ac.bd',
        }, format='json')
        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert data['data']['name'] == 'BUET'
        assert data['data']['settings'] is not None

    def test_settings_auto_created(self, auth_super_admin):
        url = reverse('university-list-create')
        res = auth_super_admin.post(url, {'name': 'DU'}, format='json')
        assert res.status_code == 201
        assert res.json()['data']['settings']['allow_ai_generation'] is True

    def test_duplicate_name_rejected(self, auth_super_admin, sample_university):
        url = reverse('university-list-create')
        res = auth_super_admin.post(url, {'name': 'Test University'}, format='json')
        assert res.status_code == 400


@pytest.mark.django_db
class TestUniversityAdminAssignment:

    def test_assign_university_admin(self, auth_super_admin, sample_university, university_admin_user):
        url = reverse('university-admin-list', kwargs={'university_id': sample_university.id})
        res = auth_super_admin.post(url, {
            'user_id': str(university_admin_user.id),
            'is_primary': True,
        }, format='json')
        assert res.status_code == 201
        assert res.json()['data']['is_primary'] is True

    def test_cannot_assign_non_admin_role_user(self, auth_super_admin, sample_university, roles):
        lecturer = User.objects.create_user(
            email='lec@test.com', password='pass',
            first_name='L', last_name='E',
            role=roles['lecturer'],
        )
        url = reverse('university-admin-list', kwargs={'university_id': sample_university.id})
        res = auth_super_admin.post(url, {'user_id': str(lecturer.id)}, format='json')
        assert res.status_code == 400
