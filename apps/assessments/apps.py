"""
Assessments App Configuration
==============================
"""
from django.apps import AppConfig

class AssessmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.assessments'
    verbose_name = '3. Assessments & Exams'

    def ready(self):
        import apps.assessments.signals  # noqa: F401
