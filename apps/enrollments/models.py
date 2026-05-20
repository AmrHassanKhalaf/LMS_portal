"""
Enrollments Models
===================

WHY THIS FILE EXISTS:
    Manages the relationship between Students and the Academic Catalog.
    Tracks which courses a student is enrolled in, their grades, and
    calculates their overall Academic Record (GPA).

DATABASE SCHEMA & RELATIONSHIPS:
    1. CourseEnrollment: The junction table linking a Student to a Course.
       - Foreign Key to students.Student
       - Foreign Key to academics.Course
       - final_grade (A, B, C, D, F) used for GPA calculation.
    2. AcademicRecord: A one-to-one profile extending the Student.
       - OneToOne Field to students.Student
       - Caches calculated cumulative_gpa and total_credits_earned.

BUSINESS LOGIC & GPA CALCULATION:
    The `save` method on CourseEnrollment acts as a trigger. When a grade
    is assigned or updated, it automatically recalculates the student's
    cumulative GPA and total credits in the AcademicRecord table.
"""

from django.db import models
from django.db.models import Sum
from apps.students.models import Student
from apps.academics.models import Course

class CourseEnrollment(models.Model):
    STATUS_CHOICES = [
        ('ENROLLED', 'Enrolled'),
        ('DROPPED', 'Dropped'),
        ('COMPLETED', 'Completed'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    GRADE_POINTS = {
        'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'F': 0.0,
    }
    
    GRADE_CHOICES = [(grade, grade) for grade in GRADE_POINTS.keys()]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ENROLLED')
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Calculated total percentage (0-100)")
    final_grade = models.CharField(max_length=2, choices=GRADE_CHOICES, null=True, blank=True)
    is_flagged_weak = models.BooleanField(default=False)
    weak_reason = models.CharField(max_length=255, blank=True)
    
    class Meta:
        # A student cannot enroll in the same exact course offering twice
        unique_together = ['student', 'course']
        ordering = ['-enrollment_date']
        
    def __str__(self):
        return f"{self.student.full_name} -> {self.course}"
        
    def save(self, *args, **kwargs):
        # Determine letter grade from overall score if not manually overridden
        if self.overall_score is not None:
            self.final_grade = self.score_to_letter_grade(self.overall_score)
                
        super().save(*args, **kwargs)
        # Recalculate GPA whenever a grade is saved/updated
        self.update_academic_record()
        
    def compute_overall_score(self):
        """
        Dynamically calculate the overall score based on Assignments and Quizzes.
        Uses a simple percentage: (Total Points Earned / Total Points Possible) * 100
        """
        from apps.assessments.models import Submission, QuizAttempt, SubjectQuizAttempt

        # Count graded assignments only. A submitted but ungraded assignment should
        # not lower the student's GPA before the teacher reviews it.
        assignment_submissions = Submission.objects.filter(
            student=self.student,
            assignment__course=self.course,
            score__isnull=False,
        )
        earned_assign = assignment_submissions.aggregate(total=Sum('score'))['total'] or 0
        possible_assign = assignment_submissions.aggregate(total=Sum('assignment__max_score'))['total'] or 0

        # Count completed/scored quiz attempts only.
        quiz_attempts = QuizAttempt.objects.filter(
            student=self.student,
            quiz__course=self.course,
            score__isnull=False,
        )
        earned_quiz = quiz_attempts.aggregate(total=Sum('score'))['total'] or 0
        possible_quiz = quiz_attempts.aggregate(total=Sum('quiz__total_marks'))['total'] or 0

        # Subject-level quizzes are also part of the subject grade. They are
        # matched to this enrollment through the course subject.
        subject_quiz_attempts = SubjectQuizAttempt.objects.filter(
            student=self.student,
            quiz__subject=self.course.subject,
            score__isnull=False,
        )
        earned_subject_quiz = subject_quiz_attempts.aggregate(total=Sum('score'))['total'] or 0
        possible_subject_quiz = subject_quiz_attempts.aggregate(total=Sum('quiz__total_marks'))['total'] or 0

        total_earned = earned_assign + earned_quiz + earned_subject_quiz
        total_possible = possible_assign + possible_quiz + possible_subject_quiz

        if total_possible > 0:
            self.overall_score = round((total_earned / total_possible) * 100, 2)
        else:
            self.overall_score = None
            self.final_grade = None
            
        self.save()  # This triggers the letter grade assignment and GPA recalc

    @classmethod
    def score_to_letter_grade(cls, score):
        if score >= 90:
            return 'A'
        if score >= 80:
            return 'B'
        if score >= 70:
            return 'C'
        if score >= 60:
            return 'D'
        return 'F'

    def update_academic_record(self):
        """
        Calculates cumulative GPA based on completed courses with grades.
        Formula: sum(grade_points * credits) / total_credits
        """
        record, created = AcademicRecord.objects.get_or_create(student=self.student)
        
        # GPA is a 4.0 scale and reflects any approved enrollment that has
        # graded work, so quizzes/assignment grades show up immediately.
        graded_enrollments = CourseEnrollment.objects.filter(
            student=self.student, 
            status__in=['ENROLLED', 'COMPLETED'],
            final_grade__isnull=False
        )
        
        total_points = 0.0
        total_credits = 0
        
        for enrollment in graded_enrollments:
            credits = enrollment.course.subject.credits
            grade_val = self.GRADE_POINTS.get(enrollment.final_grade, 0.0)
            
            total_points += float(grade_val) * credits
            total_credits += credits
            
        record.total_credits_earned = total_credits
        record.cumulative_gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
        record.save()

class AcademicRecord(models.Model):
    """
    Extends the Student model to store cached academic performance data.
    This avoids recalculating GPA on every page load (Scalability).
    """
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='academic_record')
    cumulative_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_credits_earned = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Record: {self.student.full_name} (GPA: {self.cumulative_gpa})"
