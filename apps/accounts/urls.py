"""
Accounts URL Configuration
============================

URL PATTERNS:
    /accounts/register/          → Student self-registration
    /accounts/login/             → Login (all roles)
    /accounts/logout/            → Logout action
    /accounts/create-teacher/    → Admin creates teacher (admin-only)
    /accounts/password-reset/    → Password reset flow (4 steps)
"""

from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'

urlpatterns = [
    # ---- Registration & Authentication ----
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ---- Admin: Create Teacher Account ----
    path('create-teacher/', views.create_teacher_view, name='create_teacher'),
    path('admin-teachers/', views.admin_teacher_panel, name='admin_teacher_panel'),
    path('admin-users/', views.admin_user_list, name='admin_user_list'),
    path('admin-users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),

    # ---- Password Reset Flow ----
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            email_template_name='accounts/password_reset_email.html',
            success_url='/accounts/password-reset/done/',
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/accounts/password-reset-complete/',
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]
