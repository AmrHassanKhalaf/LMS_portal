"""
Assessments Models
===================

WHY THIS FILE EXISTS:
    Manages all evaluative components of a course: Assignments, Quizzes,
    and Exams, as well as the students' submissions and grades for them.

DATABASE SCHEMA & RELATIONSHIPS:
    1. Assignment: Linked to a specific Course. Has instructions, due date,
       and optional file attachment.
    2. Submission: Linked to an Assignment and a Student. Tracks upload time,
       file content, grade received, and professor feedback.

SCALABILITY:
    The Submission table grows exponentially (Courses * Students * Assignments).
    We use `unique_together` to prevent duplicate submissions and index the fields.
    File uploads use dynamic paths to organize files by course and assignment,
    preventing massive flat directories.
"""

from django.db import models
from apps.academics.models import Course, Subject
from apps.students.models import Student

def assignment_upload_path(instance, filename):
    return f"assignments/course_{instance.course.id}/{filename}"

def submission_upload_path(instance, filename):
    return f"submissions/course_{instance.assignment.course.id}/assign_{instance.assignment.id}/stu_{instance.student.admission_number}_{filename}"

class Assignment(models.Model):
    TYPES = [
        ('HOMEWORK', 'Homework'),
        ('PROJECT', 'Project'),
        ('QUIZ', 'Quiz'),
        ('EXAM', 'Exam'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    assignment_type = models.CharField(max_length=20, choices=TYPES, default='HOMEWORK')
    description = models.TextField()
    due_date = models.DateTimeField()
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    attachment = models.FileField(upload_to=assignment_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['due_date']
        
    def __str__(self):
        return f"{self.title} ({self.course})"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    file_attachment = models.FileField(upload_to=submission_upload_path)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']
        
    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title}"
        
    @property
    def is_late(self):
        return self.submitted_at > self.assignment.due_date

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    time_limit_minutes = models.PositiveIntegerField(default=60)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    passing_score = models.DecimalField(max_digits=5, decimal_places=2, default=60.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} - {self.course}"

class Question(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES, default='MCQ')
    points = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)

    def __str__(self):
        return f"Q: {self.text[:50]}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ['quiz', 'student']

    def __str__(self):
        return f"{self.student.full_name} - {self.quiz.title}"

class SubjectQuiz(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_quizzes')
    title = models.CharField(max_length=200)
    num_questions = models.PositiveIntegerField(default=5, help_text="Number of questions required for this quiz")
    time_limit_minutes = models.PositiveIntegerField(default=60)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    passing_score = models.DecimalField(max_digits=5, decimal_places=2, default=60.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.subject.code}"

    @property
    def is_complete(self):
        """Returns True if the quiz has the required number of questions."""
        return self.questions.count() >= self.num_questions

    @property
    def questions_remaining(self):
        """Returns how many more questions the teacher needs to add."""
        return max(0, self.num_questions - self.questions.count())

class SubjectQuestion(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
    ]
    quiz = models.ForeignKey(SubjectQuiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES, default='MCQ')
    points = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)

    def __str__(self):
        return f"Q: {self.text[:50]}"

class SubjectChoice(models.Model):
    question = models.ForeignKey(SubjectQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class SubjectQuizAttempt(models.Model):
    quiz = models.ForeignKey(SubjectQuiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subject_quiz_attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ['quiz', 'student']

    def __str__(self):
        return f"{self.student.full_name} - {self.quiz.title}"
