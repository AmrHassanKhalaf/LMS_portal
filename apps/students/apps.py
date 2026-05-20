"""
Students App Configuration
============================

WHY THIS FILE EXISTS:
    AppConfig tells Django how to find and name this app.
    The 'name' must match the full Python import path.
"""

from django.apps import AppConfig


class StudentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.students'
    verbose_name = 'Student Management'
