from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.roles.models import Role, RoleChoices

User = get_user_model()


class Command(BaseCommand):
    help = 'Create the initial Super Admin user'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='admin@assessmentai.com')
        parser.add_argument('--password', type=str, default='Admin@123456')
        parser.add_argument('--first-name', type=str, default='Super')
        parser.add_argument('--last-name', type=str, default='Admin')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        if User.all_objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'User {email} already exists. Skipping.'))
            return

        try:
            role = Role.objects.get(name=RoleChoices.SUPER_ADMIN)
        except Role.DoesNotExist:
            raise CommandError('Super Admin role not found. Run: python manage.py seed_roles first.')

        user = User(
            email=email,
            first_name=options['first_name'],
            last_name=options['last_name'],
            role=role,
            is_active=True,
            is_staff=True,
            is_superuser=True,
            is_email_verified=True,
        )
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS(
            f'\nSuper Admin created successfully!'
            f'\n  Email:    {email}'
            f'\n  Password: {password}'
            f'\n\nChange this password immediately in production!'
        ))
