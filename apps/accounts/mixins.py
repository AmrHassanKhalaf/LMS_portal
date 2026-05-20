"""
Role-Based Mixins for Class-Based Views
=========================================

WHY THIS FILE EXISTS:
    Class-Based Views can't use function decorators directly on the class.
    Django provides UserPassesTestMixin for exactly this purpose.
    These mixins are the CBV equivalent of our decorators.

HOW THEY WORK:
    1. UserPassesTestMixin calls test_func() before the view executes.
    2. If test_func() returns False → handle_no_permission() is called.
    3. We override handle_no_permission() to render a 403 page
       instead of redirecting to login (which would be confusing for
       logged-in users who simply lack the right role).

USAGE:
    class AdminSettingsView(AdminRequiredMixin, TemplateView):
        ...

    class GradeStudentsView(TeacherRequiredMixin, UpdateView):
        ...

IMPORTANT:
    The mixin MUST be listed BEFORE the view class in the inheritance chain:
        class MyView(AdminRequiredMixin, ListView)   ← CORRECT
        class MyView(ListView, AdminRequiredMixin)    ← WRONG
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Base mixin that checks if the user has a specific role.
    Subclasses define `allowed_roles`.
    """
    allowed_roles = []

    def test_func(self):
        """
        Called by UserPassesTestMixin before the view runs.
        Returns True if user's role is in allowed_roles.
        """
        user = self.request.user
        return (
            user.is_authenticated
            and hasattr(user, 'profile')
            and user.profile.role in self.allowed_roles
        )

    def handle_no_permission(self):
        """
        Render a 403 page instead of redirecting to login.

        WHY override this?
            The default behavior redirects to LOGIN_URL, which is confusing
            for a user who IS logged in but lacks the role.
            A 403 page clearly communicates "you don't have permission."
        """
        if self.request.user.is_authenticated:
            return render(self.request, 'errors/403.html', status=403)
        return super().handle_no_permission()


class AdminRequiredMixin(RoleRequiredMixin):
    """Only users with role='admin' can access this view."""
    allowed_roles = ['admin']


class TeacherRequiredMixin(RoleRequiredMixin):
    """Only users with role='teacher' can access this view."""
    allowed_roles = ['teacher']


class StudentRequiredMixin(RoleRequiredMixin):
    """Only users with role='student' can access this view."""
    allowed_roles = ['student']


class StaffRequiredMixin(RoleRequiredMixin):
    """Admin OR Teacher can access this view."""
    allowed_roles = ['admin', 'teacher']
