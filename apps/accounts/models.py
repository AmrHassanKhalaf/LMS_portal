"""
Accounts Models — Profile & Role-Based Access Control
=======================================================

WHY THIS FILE EXISTS:
    Implements the RBAC (Role-Based Access Control) system via a Profile
    model that extends Django's built-in User model.

ARCHITECTURE DECISION:
    We use a OneToOneField Profile + Django Groups instead of a custom
    User model because the project already has applied auth migrations.
    Swapping the User model mid-project would require dropping all
    auth-related tables — extremely destructive.

HOW ROLES WORK:
    1. Every User gets a Profile via a post_save signal.
    2. The Profile stores a `role` field ('admin', 'teacher', 'student').
    3. On save, the Profile auto-assigns the user to the matching Django Group.
    4. Views check `request.user.profile.role` via decorators/mixins.
    5. Templates check `{% if user.profile.is_admin %}` for conditional UI.

SECURITY FLOW:
    User logs in → profile.role checked → redirected to role dashboard
    User accesses a view → decorator/mixin checks role → 403 if unauthorized
"""

from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Extends the built-in User model with role information.

    WHY OneToOneField instead of AbstractUser?
        - Project already has migrations; can't swap User model.
        - OneToOne is non-destructive and easily reversible.
        - Django's Group system handles permissions natively.
    """

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    # ---- Role Helper Properties ----
    # These make template and view checks clean and readable.

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_staff_role(self):
        """Admin or Teacher — can manage academic content."""
        return self.role in ('admin', 'teacher')

    def save(self, *args, **kwargs):
        """
        Auto-assign the user to the correct Django Group on save.

        WHY here and not in a signal?
            Because the role can change (e.g., promoting a user).
            Doing it in save() ensures group membership stays in sync.
        """
        super().save(*args, **kwargs)
        self._sync_group()

    def _sync_group(self):
        """
        Ensure the user belongs to exactly one role group.
        Removes from all role groups first, then adds to the correct one.
        """
        role_group_names = ['Admin', 'Teacher', 'Student']

        # Remove from all role groups
        for group_name in role_group_names:
            group, _ = Group.objects.get_or_create(name=group_name)
            self.user.groups.remove(group)

        # Add to correct group
        group_name_map = {
            'admin': 'Admin',
            'teacher': 'Teacher',
            'student': 'Student',
        }
        target_group_name = group_name_map.get(self.role)
        if target_group_name:
            group, _ = Group.objects.get_or_create(name=target_group_name)
            self.user.groups.add(group)

        # Admins get is_staff for Django admin panel access
        if self.role == 'admin':
            if not self.user.is_staff:
                User.objects.filter(pk=self.user.pk).update(is_staff=True)
        else:
            if self.user.is_staff and not self.user.is_superuser:
                User.objects.filter(pk=self.user.pk).update(is_staff=False)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal: Automatically create a Profile when a User is created.

    WHY a signal?
        Ensures every User always has a Profile, even if created
        via the admin panel, shell, or management command.
    """
    if created:
        # Superusers get admin role automatically
        role = 'admin' if instance.is_superuser else 'student'
        Profile.objects.get_or_create(user=instance, defaults={'role': role})


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal: Save the Profile whenever the User is saved.
    Ensures profile stays in sync.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
