"""
Students Admin Configuration
=============================

WHY THIS FILE EXISTS:
    Configures how the Student model appears in the Django admin panel.
    The admin panel is for internal staff, not regular users.

DESIGN DECISIONS:
    1. list_display controls columns shown in the list view.
    2. search_fields enables a search box for quick lookups.
    3. list_filter adds a sidebar to filter by categorical data.
    4. fieldsets organizes the detail view into logical sections.
"""

from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Customizing the admin interface for the Student model.
    """
    
    # What columns to show in the list view
    list_display = (
        'admission_number', 
        'first_name', 
        'last_name', 
        'academic_level', 
        'status', 
        'enrollment_date'
    )
    
    # Fields that can be clicked to go to the detail view
    list_display_links = ('admission_number', 'first_name', 'last_name')
    
    # Add a search box that searches these specific fields
    search_fields = ('admission_number', 'first_name', 'last_name', 'email')
    
    # Add a right sidebar to filter by these fields
    list_filter = ('status', 'academic_level', 'gender')
    
    # Default ordering in the admin panel
    ordering = ('-created_at',)
    
    # Group fields into sections on the detail page
    fieldsets = (
        ('Basic Information', {
            'fields': ('admission_number', 'first_name', 'last_name', 'email', 'image')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'gender', 'phone_number', 'address')
        }),
        ('Academic Data', {
            'fields': ('academic_level', 'enrollment_date', 'status')
        }),
        ('System Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), # Hide by default, click to expand
        }),
    )
    
    # These fields are auto-managed, so they must be read-only in admin
    readonly_fields = ('created_at', 'updated_at')

# Customize the main Admin panel headers
admin.site.site_header = "Student Management System Admin"
admin.site.site_title = "SMS Admin Portal"
admin.site.index_title = "Welcome to the SMS Administration"
