"""
Management Command: setup_groups
==================================

WHY THIS EXISTS:
    Creates the initial Django Groups (Admin, Teacher, Student) and
    creates Profile records for any existing users who don't have one.

USAGE:
    python manage.py setup_groups

WHEN TO RUN:
    - After deploying for the first time.
    - After applying the Profile migration.
    - Safe to run multiple times (idempotent).
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from apps.accounts.models import Profile


class Command(BaseCommand):
    help = 'Create role groups and profiles for existing users'

    def handle(self, *args, **options):
        # Create groups
        for group_name in ['Admin', 'Teacher', 'Student']:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {group_name}'))
            else:
                self.stdout.write(f'Group already exists: {group_name}')

        # Create profiles for existing users
        users_without_profile = User.objects.filter(profile__isnull=True)
        for user in users_without_profile:
            role = 'admin' if user.is_superuser else 'student'
            Profile.objects.create(user=user, role=role)
            self.stdout.write(self.style.SUCCESS(
                f'Created profile for {user.username} (role: {role})'
            ))

        total = users_without_profile.count()
        if total == 0:
            self.stdout.write('All users already have profiles.')

        self.stdout.write(self.style.SUCCESS('\nSetup complete!'))
