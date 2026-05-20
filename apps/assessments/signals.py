from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.enrollments.models import CourseEnrollment
from .models import QuizAttempt, SubjectQuizAttempt, Submission


@receiver(post_save, sender=Submission)
def refresh_grade_after_submission(sender, instance, **kwargs):
    if instance.score is None:
        return
    enrollment = CourseEnrollment.objects.filter(
        student=instance.student,
        course=instance.assignment.course,
    ).first()
    if enrollment:
        enrollment.compute_overall_score()


@receiver(post_save, sender=QuizAttempt)
def refresh_grade_after_quiz_attempt(sender, instance, **kwargs):
    if instance.score is None:
        return
    enrollment = CourseEnrollment.objects.filter(
        student=instance.student,
        course=instance.quiz.course,
    ).first()
    if enrollment:
        enrollment.compute_overall_score()


@receiver(post_save, sender=SubjectQuizAttempt)
def refresh_grade_after_subject_quiz_attempt(sender, instance, **kwargs):
    if instance.score is None:
        return
    enrollments = CourseEnrollment.objects.filter(
        student=instance.student,
        course__subject=instance.quiz.subject,
        status__in=['ENROLLED', 'COMPLETED'],
    )
    for enrollment in enrollments:
        enrollment.compute_overall_score()
