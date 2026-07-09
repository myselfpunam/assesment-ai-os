from django.core.management.base import BaseCommand
from apps.roles.models import Role, RoleChoices


class Command(BaseCommand):
    help = 'Seed the database with default system roles'

    ROLES = [
        {
            'name': RoleChoices.SUPER_ADMIN,
            'display_name': 'Super Admin',
            'description': 'Platform-level administrator with full access.',
        },
        {
            'name': RoleChoices.UNIVERSITY_ADMIN,
            'display_name': 'University Admin',
            'description': 'Manages university structure: departments, programmes, courses, students.',
        },
        {
            'name': RoleChoices.LECTURER,
            'display_name': 'Lecturer',
            'description': 'Uploads resources, creates quizzes, reviews questions.',
        },
        {
            'name': RoleChoices.REVIEWER,
            'display_name': 'Reviewer',
            'description': 'Reviews and approves AI-generated questions.',
        },
        {
            'name': RoleChoices.STUDENT,
            'display_name': 'Student',
            'description': 'Attempts quizzes and views results.',
        },
    ]

    def handle(self, *args, **options):
        created_count = 0
        for role_data in self.ROLES:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'display_name': role_data['display_name'],
                    'description': role_data['description'],
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created role: {role.display_name}'))
            else:
                self.stdout.write(f'  Role already exists: {role.display_name}')

        self.stdout.write(self.style.SUCCESS(f'\nDone. {created_count} new roles created.'))
