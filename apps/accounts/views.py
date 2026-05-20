"""
Accounts Views — Authentication & Role-Based Routing
======================================================

WHY THIS FILE EXISTS:
    Handles registration, login, logout, and role-based redirects.

RBAC FLOW:
    1. Registration: Only creates STUDENT accounts. Role assigned in view.
    2. Login: Same form for all roles. get_success_url() checks profile.role
       and redirects to the correct dashboard.
    3. Teacher Creation: Admin-only view that creates teacher accounts.

SECURITY:
    - Registration auto-assigns 'student' role (cannot be tampered with).
    - Teacher creation is protected by @admin_required decorator.
    - Login redirect is server-side — users can't manipulate it.
"""

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from .forms import AdminUserEditForm, UserRegisterForm, TeacherCreationForm, UserLoginForm
from .decorators import admin_required


def register_view(request):
    """
    Handle STUDENT self-registration.

    RBAC LOGIC:
        1. Creates a User object.
        2. The post_save signal auto-creates a Profile with role='student'.
        3. The student is redirected to login.

    SECURITY:
        The role is NEVER set from form data — it's hardcoded as 'student'
        in the signal. Even if a malicious user added a 'role' field to
        the HTML form, it would be ignored.
    """
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # Profile is auto-created by signal with role='student'
            username = form.cleaned_data.get('username')
            messages.success(
                request,
                f'Student account created for {username}! You can now log in.'
            )
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()

    context = {'form': form, 'title': 'Student Registration'}
    return render(request, 'accounts/register.html', context)


class CustomLoginView(LoginView):
    """
    Login view with ROLE-BASED REDIRECT.

    RBAC LOGIC:
        After successful authentication, get_success_url() checks
        the user's profile.role and redirects accordingly:
        - admin → admin dashboard (students:dashboard)
        - teacher → teacher dashboard (academics:teacher_dashboard)
        - student → student dashboard (students:student_dashboard)

    WHY not separate login pages per role?
        One login page is cleaner UX. The redirect logic handles routing.
        Separate login pages would duplicate code without adding security.
    """
    template_name = 'accounts/login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        """Role-based redirect after login."""
        user = self.request.user
        if hasattr(user, 'profile'):
            if user.profile.is_admin:
                return reverse_lazy('students:dashboard')
            elif user.profile.is_teacher:
                return reverse_lazy('academics:teacher_dashboard')
            elif user.profile.is_student:
                return reverse_lazy('students:student_dashboard')
        return reverse_lazy('students:dashboard')

    def get_redirect_url(self):
        """Override to handle already-authenticated users with role redirect."""
        return self.get_success_url()

    def form_valid(self, form):
        messages.success(self.request, 'Welcome back!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Invalid username or password. Please try again.'
        )
        return super().form_invalid(form)


def logout_view(request):
    """Log the user out and redirect to login page."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@admin_required
def create_teacher_view(request):
    """
    Admin-only view: Create a new teacher account.

    RBAC LOGIC:
        1. @admin_required ensures only admins can access this.
        2. Creates a User object via TeacherCreationForm.
        3. Sets the profile role to 'teacher'.

    SECURITY:
        The role is set SERVER-SIDE after form validation.
        The form itself has no role field — no privilege escalation possible.
    """
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Update profile to teacher role
            user.profile.role = 'teacher'
            user.profile.save()
            messages.success(
                request,
                f'Teacher account created for {user.get_full_name() or user.username}!'
            )
            return redirect('students:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TeacherCreationForm()

    context = {'form': form, 'title': 'Create Teacher Account'}
    return render(request, 'accounts/create_teacher.html', context)


@admin_required
def admin_teacher_panel(request):
    from apps.academics.models import Course
    from apps.enrollments.models import CourseEnrollment

    teachers = User.objects.filter(profile__role='teacher').order_by('username')
    teacher_cards = []
    for teacher in teachers:
        courses = Course.objects.filter(professor=teacher).select_related('subject', 'semester')
        student_count = CourseEnrollment.objects.filter(
            course__professor=teacher,
            status='ENROLLED',
        ).values('student').distinct().count()
        teacher_cards.append({
            'user': teacher,
            'courses': courses,
            'course_count': courses.count(),
            'student_count': student_count,
        })

    return render(request, 'accounts/admin_teacher_panel.html', {
        'teacher_cards': teacher_cards,
        'title': 'Teachers Admin',
    })


@admin_required
def admin_user_list(request):
    users = User.objects.select_related('profile').order_by('profile__role', 'username')
    role = request.GET.get('role', '')
    query = request.GET.get('q', '').strip()
    if role:
        users = users.filter(profile__role=role)
    if query:
        users = users.filter(
            username__icontains=query
        ) | users.filter(
            first_name__icontains=query
        ) | users.filter(
            last_name__icontains=query
        ) | users.filter(
            email__icontains=query
        )
        users = users.distinct()

    return render(request, 'accounts/admin_user_list.html', {
        'users': users,
        'role': role,
        'query': query,
        'title': 'User Management',
    })


@admin_required
def admin_user_edit(request, user_id):
    user = get_object_or_404(User.objects.select_related('profile'), id=user_id)
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'{user.username} updated successfully.')
            return redirect('accounts:admin_user_list')
    else:
        form = AdminUserEditForm(instance=user)

    return render(request, 'accounts/admin_user_form.html', {
        'form': form,
        'managed_user': user,
        'title': f'Edit User: {user.username}',
    })


def _redirect_by_role(user):
    """Helper: redirect an authenticated user to their role-specific dashboard."""
    if hasattr(user, 'profile'):
        if user.profile.is_admin:
            return redirect('students:dashboard')
        elif user.profile.is_teacher:
            return redirect('academics:teacher_dashboard')
        elif user.profile.is_student:
            return redirect('students:student_dashboard')
    return redirect('students:dashboard')
