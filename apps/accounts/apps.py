"""
Accounts App Configuration
===========================

WHY THIS FILE EXISTS:
    Django uses AppConfig to register apps and configure metadata.
    The 'name' must match the Python import path (apps.accounts).
    'default_auto_field' ensures all models use BigAutoField for IDs.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'User Accounts'
