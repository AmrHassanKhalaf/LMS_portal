"""
Student Model
==============

WHY THIS FILE EXISTS:
    Models define the database schema. Each model class maps to a
    database table. Django's ORM translates Python code into SQL
    automatically.

HOW DATA FLOWS:
    1. User fills out a form (forms.py)
    2. View validates data (views.py)
    3. Model saves to database (models.py ← YOU ARE HERE)
    4. Template displays data (templates/)

DATABASE TABLE:
    This creates a table called 'students_student' with columns:
    id, admission_number, first_name, last_name, email, date_of_birth,
    gender, phone_number, address, image, enrollment_date, grade,
    status, created_at, updated_at

DESIGN DECISIONS:
    1. admission_number is unique — prevents duplicate entries
    2. image upload uses a callable path to organize files by student
    3. created_at/updated_at track record history automatically
    4. __str__ returns full name for readability in admin and shell
    5. Meta.ordering ensures consistent display order
"""

from django.db import models
from django.urls import reverse
from django.utils import timezone


def student_image_upload_path(instance, filename):
    """
    Generate a clean upload path for student images.

    Example: media/student_images/STU001_john_doe.jpg

    WHY a function instead of a plain string?
        - Organizes files with meaningful names
        - Prevents filename collisions
        - Makes it easy to find a student's image on disk
    """
    extension = filename.split('.')[-1]
    clean_name = f"{instance.admission_number}_{instance.first_name}_{instance.last_name}"
    return f"student_images/{clean_name}.{extension}"


class Student(models.Model):
    """
    Core model representing a student in the system.

    Each field maps to a database column. Field types determine
    both the database column type AND the form widget used.
    """

    # ---- Choices for constrained fields ----
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
    ]

    LEVEL_CHOICES = [
        ('Level 1', 'Level 1'),
        ('Level 2', 'Level 2'),
        ('Level 3', 'Level 3'),
        ('Level 4', 'Level 4'),
    ]

    # ---- Core Fields ----
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    admission_number = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique admission number (e.g., STU001)',
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(blank=True)

    # ---- Personal Information ----
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text='Format: YYYY-MM-DD',
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='M',
    )
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # ---- Academic Information ----
    academic_level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='Level 1',
    )
    enrollment_date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
    )

    # ---- Media ----
    image = models.ImageField(
        upload_to=student_image_upload_path,
        blank=True,
        null=True,
        help_text='Upload a student photo (optional)',
    )

    # ---- Timestamps (auto-managed) ----
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Newest students first
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        """
        Human-readable representation.
        Used in admin, shell, and template {{ student }} tags.
        """
        return f"{self.admission_number} — {self.full_name}"

    @property
    def full_name(self):
        """
        Computed property — not stored in database.
        Access it like a field: student.full_name
        """
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        """
        Returns the URL to view this student's profile.
        Used by Django's generic views and in templates:
            <a href="{{ student.get_absolute_url }}">View</a>
        """
        return reverse('students:student_detail', kwargs={'pk': self.pk})
