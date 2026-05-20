from .models import AcademicRecord, CourseEnrollment


def refresh_enrollment_grade(enrollment):
    """Recalculate one enrollment and return the refreshed object."""
    enrollment.compute_overall_score()
    enrollment.refresh_from_db()
    return enrollment


def refresh_student_grades(student):
    """Recalculate all active graded enrollments for a student."""
    enrollments = CourseEnrollment.objects.filter(
        student=student,
        status__in=['ENROLLED', 'COMPLETED'],
    ).select_related('course', 'course__subject')
    for enrollment in enrollments:
        enrollment.compute_overall_score()
    record, _ = AcademicRecord.objects.get_or_create(student=student)
    record.refresh_from_db()
    return record


def refresh_course_grades(course):
    """Recalculate grades for every enrolled student in a course."""
    enrollments = CourseEnrollment.objects.filter(
        course=course,
        status__in=['ENROLLED', 'COMPLETED'],
    ).select_related('student', 'course', 'course__subject')
    for enrollment in enrollments:
        enrollment.compute_overall_score()
    return enrollments
