"""
Academics Models
=================

WHY THIS FILE EXISTS:
    Defines the structural hierarchy of the academic institution.
    This separates the curriculum blueprint (Subject) from a
    specific offering (Course) in a given timeframe (Semester).

DATABASE SCHEMA & RELATIONSHIPS:
    1. Semester: Represents an academic term. Can be Standard or Summer.
    2. Subject: The blueprint of what is taught (e.g., CS101, 3 Credits).
    3. Course: An instance of a Subject taught in a Semester by a specific teacher.
       - Foreign Key to Subject
       - Foreign Key to Semester
       - Foreign Key to User (Professor)
    4. Timetable: The physical/virtual meeting times for a Course.
       - Foreign Key to Course

SCALABILITY:
    Instead of adding "semester" and "professor" to the Subject model,
    we create a many-to-many resolution table essentially called `Course`.
    This allows CS101 to be taught every semester without duplicating the
    subject details, saving massive database space and preventing anomalies.
"""

import os

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

class Semester(models.Model):
    TERM_CHOICES = [
        ('FALL', 'Fall'),
        ('SPRING', 'Spring'),
        ('SUMMER', 'Summer'),
        ('WINTER', 'Winter'),
    ]
    
    name = models.CharField(max_length=50, help_text="e.g., Fall 2026")
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    year = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False, help_text="Is this the active semester?")
    
    class Meta:
        ordering = ['-year', 'start_date']
        unique_together = ['term', 'year']
        
    def __str__(self):
        return f"{self.name} ({self.get_term_display()})"
        
    def save(self, *args, **kwargs):
        # Business Logic: Ensure only one semester is marked as current
        if self.is_current:
            Semester.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True, help_text="e.g., CS101")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    department = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['code']
        
    def __str__(self):
        return f"{self.code} - {self.title}"

class Course(models.Model):
    """
    A specific instance of a Subject taught in a specific Semester.
    """
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='courses')
    professor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='taught_courses')
    capacity = models.PositiveIntegerField(default=30)
    
    class Meta:
        unique_together = ['subject', 'semester']
        ordering = ['semester', 'subject']
        
    def __str__(self):
        return f"{self.subject.code} ({self.semester.name})"
        
    @property
    def is_full(self):
        # We will implement the backward relation from Enrollments later
        return self.enrollments.count() >= self.capacity

class Timetable(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        
    def __str__(self):
        return f"{self.course} - {self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}"

def material_upload_path(instance, filename):
    return f"course_materials/course_{instance.course.id}/{filename}"

class CourseMaterial(models.Model):
    """
    Materials uploaded by a Teacher for a Course.
    Supports file uploads (PDFs, docs) and URL links (videos, resources).
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file_attachment = models.FileField(upload_to=material_upload_path, blank=True, null=True)
    url_link = models.URLField(blank=True, null=True, help_text="Link to external video or resource")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} ({self.course.subject.code})"

def validate_pdf_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx']
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file extension. Only PDF and DOC files are allowed.')

def subject_book_upload_path(instance, filename):
    return f"subject_books/subject_{instance.subject.code}/{filename}"

class SubjectBook(models.Model):
    """
    Books or global materials linked directly to a Subject, distinct from a specific Course offering.
    """
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file_attachment = models.FileField(
        upload_to=subject_book_upload_path, 
        validators=[validate_pdf_extension],
        help_text="Upload PDF or DOC files. Max size should be enforced in forms."
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.title} ({self.subject.code})"

class StudentCurriculum(models.Model):
    """
    Represents a student's personal learning plan, mapping them directly to Subjects.
    """
    from apps.students.models import Student
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='curriculum')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrolled_students')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'subject']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.code}"
