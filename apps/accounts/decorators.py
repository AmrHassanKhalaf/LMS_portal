"""
Role-Based Decorators for Function-Based Views
================================================

WHY THIS FILE EXISTS:
    Django's built-in @login_required only checks "is the user logged in?"
    It does NOT check "does this user have the right role?"

    These decorators add role-level access control on top of login_required.
    They wrap views so that ONLY users with the correct role can access them.

HOW THEY WORK:
    1. First checks if user is authenticated (redirects to login if not).
    2. Then checks if user.profile.role matches the required role.
    3. If unauthorized → renders a 403 Forbidden page.

USAGE:
    @admin_required
    def admin_settings_view(request):
        ...

    @teacher_required
    def grade_students_view(request):
        ...

    @student_required
    def my_courses_view(request):
        ...
"""

from functools import wraps
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def role_required(allowed_roles):
    """
    Generic decorator factory that checks if user's role is in allowed_roles.

    Args:
        allowed_roles: A list of role strings, e.g., ['admin', 'teacher']

    Returns:
        Decorator function that wraps the view.

    INTERNAL FLOW:
        1. @login_required ensures authentication first.
        2. Then checks profile.role against allowed_roles.
        3. Returns 403 page if role doesn't match.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'profile') and request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return render(request, 'errors/403.html', status=403)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Only users with role='admin' can access this view."""
    return role_required(['admin'])(view_func)


def teacher_required(view_func):
    """Only users with role='teacher' can access this view."""
    return role_required(['teacher'])(view_func)


def student_required(view_func):
    """Only users with role='student' can access this view."""
    return role_required(['student'])(view_func)


def staff_required(view_func):
    """Admin OR Teacher can access this view."""
    return role_required(['admin', 'teacher'])(view_func)
