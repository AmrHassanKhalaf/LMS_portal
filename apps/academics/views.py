"""
Academics Views — Role-Protected Academic Pages
==================================================

RBAC ARCHITECTURE:
    - analytics_dashboard: ADMIN only.
    - teacher_dashboard: TEACHER only — shows their assigned courses.
    - semester_list, course_list: Staff (Admin + Teacher).
    - timetable_view: All authenticated users (students see their schedule).
    - assignment_list, quiz_list: All authenticated users.
    - announcement_list, notification_list: All authenticated users.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.utils import timezone

from apps.students.models import Student
from apps.students.services import ensure_student_profile
from apps.academics.models import Course, Semester, Subject, Timetable
from apps.enrollments.models import AcademicRecord, CourseEnrollment
from apps.enrollments.services import refresh_course_grades
from apps.assessments.models import Assignment, Quiz, QuizAttempt, Submission
from apps.communication.models import Announcement, Notification
from apps.accounts.decorators import admin_required, teacher_required, staff_required
from .forms import CourseForm, SemesterForm, SubjectForm, TimetableForm


@admin_required
def analytics_dashboard(request):
    """
    ADMIN Analytics Dashboard — system-wide metrics.
    Protected: Only admins can see aggregate analytics.
    """
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    avg_gpa = (
        AcademicRecord.objects
        .filter(total_credits_earned__gt=0)
        .aggregate(Avg('cumulative_gpa'))['cumulative_gpa__avg']
        or 0.0
    )
    current_semester = Semester.objects.filter(is_current=True).first()
    top_performers = AcademicRecord.objects.order_by('-cumulative_gpa')[:5]
    announcements = Announcement.objects.all()[:5]
    notifications = Notification.objects.filter(user=request.user)[:5]

    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'avg_gpa': round(avg_gpa, 2),
        'current_semester': current_semester,
        'top_performers': top_performers,
        'announcements': announcements,
        'notifications': notifications,
    }
    return render(request, 'academics/analytics_dashboard.html', context)


@admin_required
def admin_academics_panel(request):
    semesters = Semester.objects.annotate(course_count=Count('courses')).order_by('-year', 'start_date')
    subjects = Subject.objects.annotate(course_count=Count('courses')).order_by('code')
    courses = Course.objects.select_related('subject', 'semester', 'professor').annotate(
        enrolled_count=Count('enrollments', filter=Q(enrollments__status='ENROLLED'))
    ).order_by('-semester__year', 'subject__code')
    schedules = Timetable.objects.select_related(
        'course',
        'course__subject',
        'course__semester',
        'course__professor',
    ).order_by('day_of_week', 'start_time')
    teachers = User.objects.filter(profile__role='teacher').order_by('username')

    return render(request, 'academics/admin_academics_panel.html', {
        'semesters': semesters,
        'subjects': subjects,
        'courses': courses,
        'schedules': schedules,
        'teachers': teachers,
        'title': 'Academics Admin',
    })


def _save_admin_form(request, form_class, template_name, success_message, redirect_name, instance=None, extra_context=None):
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, success_message)
            return redirect(redirect_name)
    else:
        form = form_class(instance=instance)
    context = {'form': form}
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


@admin_required
def admin_semester_form(request, semester_id=None):
    semester = get_object_or_404(Semester, id=semester_id) if semester_id else None
    return _save_admin_form(
        request,
        SemesterForm,
        'academics/admin_model_form.html',
        'Semester saved successfully.',
        'academics:admin_academics_panel',
        instance=semester,
        extra_context={'title': 'Edit Semester' if semester else 'Add Semester', 'model_name': 'Semester'},
    )


@admin_required
def admin_subject_form(request, subject_id=None):
    subject = get_object_or_404(Subject, id=subject_id) if subject_id else None
    return _save_admin_form(
        request,
        SubjectForm,
        'academics/admin_model_form.html',
        'Subject saved successfully.',
        'academics:admin_academics_panel',
        instance=subject,
        extra_context={'title': 'Edit Subject' if subject else 'Add Subject', 'model_name': 'Subject'},
    )


@admin_required
def admin_course_form(request, course_id=None):
    course = get_object_or_404(Course, id=course_id) if course_id else None
    return _save_admin_form(
        request,
        CourseForm,
        'academics/admin_model_form.html',
        'Course saved successfully.',
        'academics:admin_academics_panel',
        instance=course,
        extra_context={'title': 'Edit Course' if course else 'Add Course', 'model_name': 'Course'},
    )


@admin_required
def admin_timetable_form(request, timetable_id=None):
    schedule = get_object_or_404(Timetable, id=timetable_id) if timetable_id else None
    return _save_admin_form(
        request,
        TimetableForm,
        'academics/admin_model_form.html',
        'Timetable entry saved successfully.',
        'academics:admin_academics_panel',
        instance=schedule,
        extra_context={'title': 'Edit Timetable Entry' if schedule else 'Add Timetable Entry', 'model_name': 'Timetable'},
    )


@teacher_required
def teacher_dashboard(request):
    """
    TEACHER Dashboard — shows courses they teach, pending submissions, etc.

    RBAC: Only teachers can access this.

    BUSINESS LOGIC:
        Teachers only see THEIR OWN courses (filtered by professor=request.user).
        This prevents teachers from viewing or managing other teachers' courses.
    """
    my_courses = Course.objects.filter(
        professor=request.user
    ).select_related('subject', 'semester').annotate(
        enrolled_count=Count('enrollments', filter=Q(enrollments__status='ENROLLED'))
    )
    for course in my_courses:
        refresh_course_grades(course)

    teacher_enrollments = CourseEnrollment.objects.filter(
        course__professor=request.user,
        status='ENROLLED',
    ).select_related(
        'student',
        'course',
        'course__subject',
        'course__semester',
    ).order_by('student__first_name', 'student__last_name', 'course__subject__code')

    # Pending submissions across teacher's courses
    pending_submissions = Submission.objects.filter(
        assignment__course__professor=request.user,
        score__isnull=True
    ).select_related('student', 'assignment')[:10]

    # Upcoming assignments for teacher's courses
    upcoming_assignments = Assignment.objects.filter(
        course__professor=request.user,
        due_date__gte=timezone.now()
    ).order_by('due_date')[:5]

    # Student count across teacher's courses
    total_students = CourseEnrollment.objects.filter(
        course__professor=request.user,
        status='ENROLLED'
    ).values('student').distinct().count()

    # Quizzes for teacher's courses
    my_quizzes = Quiz.objects.filter(
        course__professor=request.user
    ).select_related('course', 'course__subject')[:5]
    
    total_quizzes = Quiz.objects.filter(course__professor=request.user).count()
    total_assignments = Assignment.objects.filter(course__professor=request.user).count()

    pending_submissions_count = Submission.objects.filter(
        assignment__course__professor=request.user,
        score__isnull=True
    ).count()

    # Weak Students: automatic by low score, or manually flagged by the teacher.
    weak_students = CourseEnrollment.objects.filter(
        course__professor=request.user,
        status='ENROLLED'
    ).filter(
        Q(overall_score__lt=60) | Q(is_flagged_weak=True)
    ).select_related('student', 'course', 'course__subject')[:5]

    context = {
        'title': 'Teacher Dashboard',
        'my_courses': my_courses,
        'teacher_enrollments': teacher_enrollments,
        'pending_submissions': pending_submissions,
        'upcoming_assignments': upcoming_assignments,
        'total_students': total_students,
        'total_quizzes': total_quizzes,
        'total_assignments': total_assignments,
        'pending_submissions_count': pending_submissions_count,
        'my_quizzes': my_quizzes,
        'weak_students': weak_students,
    }
    return render(request, 'academics/teacher_dashboard.html', context)


@teacher_required
def flag_weak_student(request, enrollment_id):
    if request.method != 'POST':
        return redirect('academics:teacher_dashboard')

    enrollment = get_object_or_404(
        CourseEnrollment,
        id=enrollment_id,
        course__professor=request.user,
        status='ENROLLED',
    )
    enrollment.is_flagged_weak = True
    enrollment.weak_reason = request.POST.get('weak_reason', '').strip()[:255]
    enrollment.save(update_fields=['is_flagged_weak', 'weak_reason'])
    messages.success(request, f'{enrollment.student.full_name} was added to Weak Students Focus.')
    return redirect('academics:teacher_dashboard')


@teacher_required
def unflag_weak_student(request, enrollment_id):
    if request.method != 'POST':
        return redirect('academics:teacher_dashboard')

    enrollment = get_object_or_404(
        CourseEnrollment,
        id=enrollment_id,
        course__professor=request.user,
    )
    enrollment.is_flagged_weak = False
    enrollment.weak_reason = ''
    enrollment.save(update_fields=['is_flagged_weak', 'weak_reason'])
    messages.success(request, f'{enrollment.student.full_name} was removed from Weak Students Focus.')
    return redirect('academics:teacher_dashboard')


@staff_required
def semester_list(request):
    semesters = Semester.objects.all()
    return render(request, 'academics/semester_list.html', {'semesters': semesters})


@staff_required
def course_list(request):
    courses = Course.objects.select_related('subject', 'semester', 'professor').annotate(
        enrolled_count=Count('enrollments', filter=Q(enrollments__status='ENROLLED'))
    )
    if hasattr(request.user, 'profile') and request.user.profile.is_teacher:
        courses = courses.filter(professor=request.user)
    return render(request, 'academics/course_list.html', {'courses': courses})


@login_required
def timetable_view(request):
    current_semester = Semester.objects.filter(is_current=True).first()
    if current_semester:
        schedules = Timetable.objects.filter(
            course__semester=current_semester
        ).select_related('course', 'course__subject').order_by('day_of_week', 'start_time')
        if hasattr(request.user, 'profile') and request.user.profile.is_teacher:
            schedules = schedules.filter(course__professor=request.user)
        elif hasattr(request.user, 'profile') and request.user.profile.is_student:
            student = ensure_student_profile(request.user)
            enrolled_course_ids = CourseEnrollment.objects.filter(
                student=student,
                status='ENROLLED',
            ).values_list('course_id', flat=True)
            schedules = schedules.filter(course_id__in=enrolled_course_ids)
    else:
        schedules = Timetable.objects.none()
    page_title = 'Timetable'
    if hasattr(request.user, 'profile') and not request.user.profile.is_admin:
        page_title = 'My Schedule'
    return render(request, 'academics/timetable.html', {
        'schedules': schedules,
        'current_semester': current_semester,
        'title': page_title,
    })


@login_required
def assignment_list(request):
    assignments = Assignment.objects.select_related('course', 'course__subject')
    submitted_assignment_ids = []

    if hasattr(request.user, 'profile') and request.user.profile.is_teacher:
        assignments = assignments.filter(course__professor=request.user)
    elif hasattr(request.user, 'profile') and request.user.profile.is_student:
        student = ensure_student_profile(request.user)
        enrolled_course_ids = CourseEnrollment.objects.filter(
            student=student,
            status='ENROLLED',
        ).values_list('course_id', flat=True)
        assignments = assignments.filter(course_id__in=enrolled_course_ids)
        submitted_assignment_ids = list(
            Submission.objects.filter(student=student).values_list('assignment_id', flat=True)
        )

    return render(request, 'academics/assignment_list.html', {
        'assignments': assignments,
        'submitted_assignment_ids': submitted_assignment_ids,
    })


@login_required
def quiz_list(request):
    quizzes = Quiz.objects.select_related('course', 'course__subject')
    attempted_quiz_ids = []

    if hasattr(request.user, 'profile') and request.user.profile.is_teacher:
        quizzes = quizzes.filter(course__professor=request.user)
    elif hasattr(request.user, 'profile') and request.user.profile.is_student:
        student = ensure_student_profile(request.user)
        enrolled_course_ids = CourseEnrollment.objects.filter(
            student=student,
            status='ENROLLED',
        ).values_list('course_id', flat=True)
        quizzes = quizzes.filter(course_id__in=enrolled_course_ids)
        attempted_quiz_ids = list(
            QuizAttempt.objects.filter(student=student).values_list('quiz_id', flat=True)
        )

    return render(request, 'academics/quiz_list.html', {
        'quizzes': quizzes,
        'attempted_quiz_ids': attempted_quiz_ids,
    })


@login_required
def announcement_list(request):
    announcements = Announcement.objects.all()
    return render(request, 'academics/announcement_list.html', {'announcements': announcements})


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'academics/notification_list.html', {'notifications': notifications})


@login_required
def course_material_list(request, course_id):
    """
    List materials for a specific course.
    Teachers can see materials for their courses.
    Students can see materials for courses they are enrolled in.
    """
    from .models import CourseMaterial
    course = get_object_or_404(Course, id=course_id)
    
    # RBAC: Verify access
    if hasattr(request.user, 'profile'):
        if request.user.profile.is_teacher and course.professor != request.user:
            return render(request, 'errors/403.html', status=403)
        if request.user.profile.is_student:
            student = ensure_student_profile(request.user)
            is_enrolled = CourseEnrollment.objects.filter(student=student, course=course).exists()
            if not is_enrolled:
                return render(request, 'errors/403.html', status=403)

    materials = CourseMaterial.objects.filter(course=course)
    return render(request, 'academics/material_list.html', {'course': course, 'materials': materials})


@login_required
def material_overview(request):
    from .models import CourseMaterial

    materials = CourseMaterial.objects.select_related('course', 'course__subject', 'course__professor')
    courses = Course.objects.none()

    if hasattr(request.user, 'profile') and request.user.profile.is_teacher:
        courses = Course.objects.filter(professor=request.user).select_related('subject', 'semester')
        materials = materials.filter(course__professor=request.user)
    elif hasattr(request.user, 'profile') and request.user.profile.is_student:
        student = ensure_student_profile(request.user)
        enrolled_course_ids = CourseEnrollment.objects.filter(
            student=student,
            status='ENROLLED',
        ).values_list('course_id', flat=True)
        courses = Course.objects.filter(id__in=enrolled_course_ids).select_related('subject', 'semester')
        materials = materials.filter(course_id__in=enrolled_course_ids)

    return render(request, 'academics/material_overview.html', {
        'materials': materials,
        'courses': courses,
    })


@teacher_required
def upload_course_material(request, course_id):
    """
    Teacher only: Upload new course materials.
    """
    from django.contrib import messages
    from django.shortcuts import redirect
    from .forms import CourseMaterialForm

    course = get_object_or_404(Course, id=course_id)
    
    # RBAC: Only the professor of the course can upload
    if course.professor != request.user:
        return render(request, 'errors/403.html', status=403)

    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            messages.success(request, 'Material uploaded successfully.')
            return redirect('academics:course_material_list', course_id=course.id)
    else:
        form = CourseMaterialForm()

    return render(request, 'academics/material_form.html', {'form': form, 'course': course})


# =========================================================
# NEW: Subject Browsing & Student Curriculum
# =========================================================

@login_required
def browse_subjects(request):
    """
    Shows subjects according to the user's role.
    Students and admins see the full catalog. Teachers see only subjects for
    courses assigned to them.
    """
    from .models import StudentCurriculum

    subjects = Subject.objects.all().order_by('code')
    is_teacher_catalog = False
    if hasattr(request.user, 'profile') and request.user.profile.is_teacher:
        subjects = subjects.filter(courses__professor=request.user).distinct()
        is_teacher_catalog = True

    enrolled_subject_ids = []
    approved_subject_ids = []

    student = ensure_student_profile(request.user)

    if student:
        enrolled_subject_ids = list(
            StudentCurriculum.objects.filter(
                student=student
            ).values_list('subject_id', flat=True)
        )
        approved_subject_ids = list(
            CourseEnrollment.objects.filter(
                student=student,
                status='ENROLLED',
            ).values_list('course__subject_id', flat=True)
        )
        enrolled_subject_ids = sorted(set(enrolled_subject_ids) | set(approved_subject_ids))

    context = {
        'title': 'Browse Subjects',
        'subjects': subjects,
        'enrolled_subject_ids': enrolled_subject_ids,
        'approved_subject_ids': approved_subject_ids,
        'is_teacher_catalog': is_teacher_catalog,
    }
    return render(request, 'academics/browse_subjects.html', context)


def teacher_owns_subject(user, subject):
    return Course.objects.filter(subject=subject, professor=user).exists()


@login_required
def add_to_curriculum(request, subject_id):
    """Student adds a subject and is enrolled immediately when a course exists."""
    from django.contrib import messages
    from .models import StudentCurriculum

    if request.method != 'POST':
        return redirect('academics:browse_subjects')

    student = ensure_student_profile(request.user)
    if not student:
        return render(request, 'errors/403.html', status=403)

    subject = get_object_or_404(Subject, id=subject_id)
    _, created = StudentCurriculum.objects.get_or_create(student=student, subject=subject)

    course = (
        Course.objects.filter(subject=subject, semester__is_current=True).first()
        or Course.objects.filter(subject=subject).order_by('-semester__year', '-semester__start_date').first()
    )
    if course:
        enrollment, _ = CourseEnrollment.objects.get_or_create(
            student=student,
            course=course,
            defaults={'status': 'ENROLLED'},
        )
        if enrollment.status != 'ENROLLED':
            enrollment.status = 'ENROLLED'
            enrollment.save()

    if created:
        messages.success(request, f'"{subject.title}" has been added to your curriculum.')
    else:
        messages.info(request, f'You are already enrolled in "{subject.title}".')

    return redirect('academics:browse_subjects')


@login_required
def remove_from_curriculum(request, subject_id):
    """Student removes a subject from their personal learning plan. POST only."""
    from django.contrib import messages
    from .models import StudentCurriculum

    if request.method != 'POST':
        return redirect('academics:browse_subjects')

    student = ensure_student_profile(request.user)
    if not student:
        return render(request, 'errors/403.html', status=403)

    subject = get_object_or_404(Subject, id=subject_id)

    deleted_count, _ = StudentCurriculum.objects.filter(student=student, subject=subject).delete()
    if deleted_count:
        CourseEnrollment.objects.filter(
            student=student,
            course__subject=subject,
        ).delete()
        messages.success(request, f'❌ "{subject.title}" has been removed from your curriculum.')
    else:
        messages.warning(request, f'You were not enrolled in "{subject.title}".')

    next_url = request.POST.get('next', 'academics:browse_subjects')
    return redirect(next_url)


@login_required
def my_curriculum(request):
    """Show the student's personal curriculum / learning plan."""
    from .models import StudentCurriculum

    student = ensure_student_profile(request.user)
    if not student:
        return render(request, 'errors/403.html', status=403)

    curriculum = StudentCurriculum.objects.filter(
        student=student
    ).select_related('subject').order_by('subject__code')

    context = {
        'title': 'My Curriculum',
        'curriculum': curriculum,
    }
    return render(request, 'academics/my_curriculum.html', context)


@login_required
def subject_detail(request, subject_id):
    """
    View a Subject's books and quizzes. 
    Students must have the subject in their curriculum.
    Teachers can view only subjects attached to their assigned courses.
    """
    from .models import SubjectBook, StudentCurriculum
    from apps.assessments.models import SubjectQuiz

    subject = get_object_or_404(Subject, id=subject_id)

    if hasattr(request.user, 'profile') and request.user.profile.is_teacher:
        if not teacher_owns_subject(request.user, subject):
            return render(request, 'errors/403.html', status=403)

    # RBAC: Students must be enrolled
    student = ensure_student_profile(request.user)
    if student:
        is_enrolled = StudentCurriculum.objects.filter(
            student=student, subject=subject
        ).exists()
        if not is_enrolled:
            from django.contrib import messages
            messages.warning(request, 'You must add this subject to your curriculum first.')
            return redirect('academics:browse_subjects')

    books = SubjectBook.objects.filter(subject=subject)
    quizzes = SubjectQuiz.objects.filter(subject=subject)

    context = {
        'title': subject.title,
        'subject': subject,
        'books': books,
        'quizzes': quizzes,
    }
    return render(request, 'academics/subject_detail.html', context)


# =========================================================
# NEW: Teacher Subject Book Management
# =========================================================

@teacher_required
def upload_subject_book(request, subject_id):
    """Teacher uploads a book/document linked to a specific subject."""
    from django.contrib import messages
    from .forms import SubjectBookForm

    subject = get_object_or_404(Subject, id=subject_id)
    if not teacher_owns_subject(request.user, subject):
        return render(request, 'errors/403.html', status=403)

    if request.method == 'POST':
        form = SubjectBookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.subject = subject
            book.save()
            messages.success(request, f'Book "{book.title}" uploaded successfully!')
            return redirect('academics:subject_detail', subject_id=subject.id)
    else:
        form = SubjectBookForm()

    return render(request, 'academics/upload_subject_book.html', {
        'form': form,
        'subject': subject,
        'title': f'Upload Book — {subject.code}',
    })


@teacher_required
def delete_subject_book(request, book_id):
    """Teacher deletes a book."""
    from django.contrib import messages
    from .models import SubjectBook

    book = get_object_or_404(SubjectBook, id=book_id)
    if not teacher_owns_subject(request.user, book.subject):
        return render(request, 'errors/403.html', status=403)

    subject_id = book.subject.id
    book.delete()
    messages.success(request, 'Book deleted successfully.')
    return redirect('academics:subject_detail', subject_id=subject_id)


# =========================================================
# NEW: Teacher Subject Quiz Management
# =========================================================

@teacher_required
def create_subject_quiz(request, subject_id):
    """Teacher creates a quiz for a specific subject."""
    from django.contrib import messages
    from apps.assessments.models import SubjectQuiz

    subject = get_object_or_404(Subject, id=subject_id)
    if not teacher_owns_subject(request.user, subject):
        return render(request, 'errors/403.html', status=403)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        num_questions = request.POST.get('num_questions', 5)
        time_limit = request.POST.get('time_limit_minutes', 60)
        total_marks = request.POST.get('total_marks', 100)
        passing_score = request.POST.get('passing_score', 60)

        if title and int(num_questions) >= 1:
            quiz = SubjectQuiz.objects.create(
                subject=subject,
                title=title,
                num_questions=int(num_questions),
                time_limit_minutes=int(time_limit),
                total_marks=total_marks,
                passing_score=passing_score,
            )
            messages.success(request, f'Quiz "{quiz.title}" created! Now add {quiz.num_questions} questions.')
            return redirect('academics:manage_subject_quiz', quiz_id=quiz.id)
        else:
            messages.error(request, 'Quiz title and at least 1 question are required.')

    return render(request, 'academics/create_subject_quiz.html', {
        'subject': subject,
        'title': f'Create Quiz — {subject.code}',
    })


@teacher_required
def manage_subject_quiz(request, quiz_id):
    """
    Teacher manages questions and choices for a Subject Quiz.
    Handles adding questions and their MCQ choices via POST.
    """
    from django.contrib import messages
    from apps.assessments.models import SubjectQuiz, SubjectQuestion, SubjectChoice

    quiz = get_object_or_404(SubjectQuiz.objects.select_related('subject'), id=quiz_id)
    if not teacher_owns_subject(request.user, quiz.subject):
        return render(request, 'errors/403.html', status=403)

    current_count = quiz.questions.count()

    if request.method == 'POST':
        # Enforce question limit
        if current_count >= quiz.num_questions:
            messages.warning(request, f'This quiz already has all {quiz.num_questions} required questions.')
            return redirect('academics:manage_subject_quiz', quiz_id=quiz.id)

        question_text = request.POST.get('question_text', '').strip()
        points = request.POST.get('points', 1)
        choices_texts = request.POST.getlist('choice_text')
        correct_choice = request.POST.get('correct_choice')

        if question_text and choices_texts:
            question = SubjectQuestion.objects.create(
                quiz=quiz,
                text=question_text,
                points=points,
            )
            for i, ct in enumerate(choices_texts):
                if ct.strip():
                    SubjectChoice.objects.create(
                        question=question,
                        text=ct.strip(),
                        is_correct=(str(i) == correct_choice),
                    )
            remaining = quiz.questions_remaining
            if remaining > 0:
                messages.success(request, f'Question added! {remaining} more to go.')
            else:
                messages.success(request, '🎉 All questions added! This quiz is now complete and ready for students.')
            return redirect('academics:manage_subject_quiz', quiz_id=quiz.id)
        else:
            messages.error(request, 'Question text and at least one choice are required.')

    questions = quiz.questions.prefetch_related('choices').all()

    return render(request, 'academics/manage_subject_quiz.html', {
        'quiz': quiz,
        'questions': questions,
        'questions_remaining': quiz.questions_remaining,
        'is_complete': quiz.is_complete,
        'title': f'Manage Quiz — {quiz.title}',
    })


@teacher_required
def delete_subject_quiz(request, quiz_id):
    """Teacher deletes a Subject Quiz."""
    from django.contrib import messages
    from apps.assessments.models import SubjectQuiz

    quiz = get_object_or_404(SubjectQuiz, id=quiz_id)
    if not teacher_owns_subject(request.user, quiz.subject):
        return render(request, 'errors/403.html', status=403)

    subject_id = quiz.subject.id
    quiz.delete()
    messages.success(request, 'Quiz deleted successfully.')
    return redirect('academics:subject_detail', subject_id=subject_id)


@teacher_required
def subject_quiz_results(request, quiz_id):
    """Teacher views all student attempts/results for a specific quiz."""
    from apps.assessments.models import SubjectQuiz, SubjectQuizAttempt

    quiz = get_object_or_404(SubjectQuiz.objects.select_related('subject'), id=quiz_id)
    if not teacher_owns_subject(request.user, quiz.subject):
        return render(request, 'errors/403.html', status=403)

    attempts = SubjectQuizAttempt.objects.filter(
        quiz=quiz
    ).select_related('student').order_by('-score')

    context = {
        'quiz': quiz,
        'attempts': attempts,
        'title': f'Results — {quiz.title}',
    }
    return render(request, 'academics/subject_quiz_results.html', context)


# =========================================================
# NEW: Student Takes a Subject Quiz
# =========================================================

@login_required
def take_subject_quiz(request, quiz_id):
    """
    Student takes a Subject Quiz. Auto-grades on submission.
    """
    from django.contrib import messages
    from .models import StudentCurriculum
    from apps.assessments.models import SubjectQuiz, SubjectQuizAttempt

    student = ensure_student_profile(request.user)
    if not student:
        return render(request, 'errors/403.html', status=403)

    quiz = get_object_or_404(SubjectQuiz.objects.select_related('subject'), id=quiz_id)

    # RBAC: Student must have this subject in their curriculum
    if not StudentCurriculum.objects.filter(student=student, subject=quiz.subject).exists():
        messages.warning(request, 'You must add this subject to your curriculum first.')
        return redirect('academics:browse_subjects')

    # Block if quiz is incomplete (teacher hasn't finished adding questions)
    if not quiz.is_complete:
        messages.warning(request, 'This quiz is not yet available. The instructor is still preparing it.')
        return redirect('academics:subject_detail', subject_id=quiz.subject.id)

    # Check if already attempted
    existing_attempt = SubjectQuizAttempt.objects.filter(quiz=quiz, student=student).first()
    if existing_attempt:
        messages.info(request, f'You already took this quiz. Score: {existing_attempt.score}')
        return redirect('academics:subject_detail', subject_id=quiz.subject.id)

    questions = quiz.questions.prefetch_related('choices').all()

    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_id = request.POST.get(f'question_{question.id}')
            if selected_id:
                try:
                    selected_choice = question.choices.get(id=int(selected_id))
                    if selected_choice.is_correct:
                        score += float(question.points)
                except Exception:
                    pass

        total_possible_points = sum(float(question.points) for question in questions)
        if total_possible_points > 0:
            final_score = (score / total_possible_points) * float(quiz.total_marks)
        else:
            final_score = 0

        SubjectQuizAttempt.objects.create(
            quiz=quiz,
            student=student,
            score=round(final_score, 2),
        )
        enrollment = CourseEnrollment.objects.filter(
            student=student,
            course__subject=quiz.subject,
            status='ENROLLED',
        ).first()
        if enrollment:
            enrollment.compute_overall_score()

        messages.success(request, f'Quiz submitted! Your score: {round(final_score, 2)}/{quiz.total_marks}')
        return redirect('academics:subject_detail', subject_id=quiz.subject.id)

    return render(request, 'academics/take_subject_quiz.html', {
        'quiz': quiz,
        'questions': questions,
        'title': f'Take Quiz — {quiz.title}',
    })
