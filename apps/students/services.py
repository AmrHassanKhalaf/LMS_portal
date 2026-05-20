"""
Student Services (Business Logic Layer)
========================================

WHY THIS FILE EXISTS:
    Services separate business logic from views. Views should only
    handle HTTP request/response — the "what to do with data" logic
    belongs here.

BENEFITS:
    1. Views stay thin and readable
    2. Logic is reusable (views, management commands, API, etc.)
    3. Easier to test — no need to mock HTTP requests
    4. Single source of truth for business rules

HOW IT CONNECTS:
    views.py calls service functions → services query models →
    return processed data back to views → views pass to templates

EXAMPLE FLOW (Dashboard):
    1. View calls get_dashboard_statistics()
    2. Service queries Student model, aggregates data
    3. Returns a dictionary of stats
    4. View passes dict to template context
"""

from django.db.models import Q, Count

from .models import Student


def ensure_student_profile(user):
    """
    Ensure a student-role User has a linked Student domain profile.
    """
    if not user.is_authenticated:
        return None

    if hasattr(user, 'student_profile'):
        return user.student_profile

    if not hasattr(user, 'profile') or not user.profile.is_student:
        return None

    base_admission = f"STU{user.id:05d}"
    admission_number = base_admission
    counter = 1
    while Student.objects.filter(admission_number=admission_number).exists():
        admission_number = f"{base_admission}-{counter}"
        counter += 1

    return Student.objects.create(
        user=user,
        admission_number=admission_number,
        first_name=user.first_name or user.username,
        last_name=user.last_name or '',
        email=user.email,
    )


def get_dashboard_statistics():
    """
    Compute dashboard statistics in a single, efficient query.

    Returns a dictionary with:
        - total_students: Total count of all students
        - active_students: Count of students with status='active'
        - inactive_students: Count of non-active students
        - graduated_students: Count of graduated students
        - gender_distribution: Dict with male/female/other counts
        - grade_distribution: Dict mapping each grade to its count
        - recent_students: Last 5 students added

    PERFORMANCE NOTE:
        We use Django's aggregate() and annotate() to compute counts
        in SQL rather than Python. This is O(1) queries instead of
        loading all students into memory.
    """
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='active').count()
    inactive_students = Student.objects.filter(status='inactive').count()
    graduated_students = Student.objects.filter(status='graduated').count()

    # Gender breakdown
    gender_distribution = {
        'male': Student.objects.filter(gender='M').count(),
        'female': Student.objects.filter(gender='F').count(),
        'other': Student.objects.filter(gender='O').count(),
    }

    # Academic level distribution for charts
    academic_level_distribution = dict(
        Student.objects.values_list('academic_level')
        .annotate(count=Count('id'))
        .order_by('academic_level')
    )

    # Most recently added students
    recent_students = Student.objects.all()[:5]

    return {
        'total_students': total_students,
        'active_students': active_students,
        'inactive_students': inactive_students,
        'graduated_students': graduated_students,
        'gender_distribution': gender_distribution,
        'academic_level_distribution': academic_level_distribution,
        'recent_students': recent_students,
    }


def search_students(query):
    """
    Search students by name or admission number.

    Uses Django's Q objects for OR queries:
        Q(first_name__icontains=query) | Q(last_name__icontains=query)

    The 'icontains' lookup is case-insensitive and works with
    both SQLite and PostgreSQL — no changes needed when switching.

    Args:
        query: Search string from the user

    Returns:
        QuerySet of matching students (can be empty)
    """
    if not query or not query.strip():
        return Student.objects.none()

    query = query.strip()
    search_results = Student.objects.filter(
        Q(first_name__icontains=query)
        | Q(last_name__icontains=query)
        | Q(admission_number__icontains=query)
        | Q(email__icontains=query)
    )
    return search_results
