"""
Academics App Configuration
============================
WHY THIS FILE EXISTS:
    Configures the metadata for the academics app.
"""
from django.apps import AppConfig

class AcademicsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.academics'
    verbose_name = '1. Academics Catalog'
