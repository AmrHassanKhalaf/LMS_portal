"""
Project-Level URL Configuration
================================

WHY THIS FILE EXISTS:
    This is the ROOT URL router. Every incoming HTTP request hits this
    file first. It delegates to app-level url files using include().

HOW IT CONNECTS:
    Browser Request → config/urls.py → apps/accounts/urls.py or apps/students/urls.py

DESIGN DECISIONS:
    1. Each app has its own urls.py — keeps routing modular
    2. The root '/' redirects to the student dashboard
    3. Media files are served in development via static() helper
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def root_redirect(request):
    if request.user.is_authenticated:
        from apps.accounts.views import _redirect_by_role
        return _redirect_by_role(request.user)
    return redirect('accounts:login')

urlpatterns = [
    # Admin panel — customized in apps/students/admin.py
    path('admin/', admin.site.urls),

    # Root URL redirects to the dashboard
    path('', root_redirect, name='home'),

    # Account-related URLs: login, register, logout, password reset
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),

    # Student management URLs: CRUD + dashboard + search
    path('students/', include('apps.students.urls', namespace='students')),
    
    # API endpoints
    path('api/v1/', include('apps.api.urls', namespace='api')),

    # Academics URLs: Analytics dashboard
    path('academics/', include('apps.academics.urls', namespace='academics')),

    # Assessments URLs: Gradebook, Quizzes, Assignments
    path('assessments/', include('apps.assessments.urls', namespace='assessments')),
]

# Serve media files during development (Django's dev server only)
# In production, your web server (Nginx/WhiteNoise) handles this.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# =============================================================
# Custom Error Handlers
# =============================================================
# These point to views that render our styled error pages
# instead of Django's plain defaults.
handler404 = 'apps.students.views.custom_404_view'
handler500 = 'apps.students.views.custom_500_view'
