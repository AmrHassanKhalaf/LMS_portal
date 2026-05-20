"""
Students Views — Role-Protected CRUD & Dashboards
====================================================

RBAC ARCHITECTURE:
    - dashboard_view: ADMIN only → shows system-wide statistics.
    - student_dashboard_view: STUDENT only → shows personal academic data.
    - CRUD views (Create, Update, Delete): STAFF only (Admin or Teacher).
    - StudentDetailView: Staff sees any student; students see only themselves.
    - StudentListView: Staff only.
    - search_view: Staff only.

PERMISSION ENFORCEMENT:
    - FBVs use @admin_required, @student_required, @staff_required decorators.
    - CBVs use AdminRequiredMixin, StaffRequiredMixin, etc.
    - These are defined in apps.accounts.decorators and apps.accounts.mixins.
"""

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Avg
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Student
from .forms import StudentForm, StudentSearchForm
from . import services

from apps.accounts.decorators import admin_required, student_required, staff_required
from apps.accounts.mixins import StaffRequiredMixin, AdminRequiredMixin
from apps.assessments.models import Quiz, QuizAttempt
from apps.enrollments.models import CourseEnrollment
from apps.enrollments.services import refresh_student_grades


@admin_required
def dashboard_view(request):
    """
    ADMIN Dashboard — system-wide statistics.

    RBAC: Only users with role='admin' can access this.
    Teachers and students are redirected to 403.
    """
    stats = services.get_dashboard_statistics()
    from apps.academics.models import Course, Semester, Subject, Timetable
    from apps.assessments.models import Assignment, Quiz, Submission
    from apps.enrollments.models import AcademicRecord, CourseEnrollment

    teachers = User.objects.filter(profile__role='teacher').select_related('profile').order_by('username')[:8]
    recent_courses = Course.objects.select_related('subject', 'semester', 'professor').order_by('-id')[:8]
    current_semester = Semester.objects.filter(is_current=True).first()
    pending_grades = Submission.objects.filter(score__isnull=True).count()

    context = {
        'title': 'Admin Dashboard',
        **stats,
        'total_teachers': User.objects.filter(profile__role='teacher').count(),
        'total_users': User.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_courses': Course.objects.count(),
        'total_semesters': Semester.objects.count(),
        'total_timetable_entries': Timetable.objects.count(),
        'total_enrollments': CourseEnrollment.objects.filter(status='ENROLLED').count(),
        'total_assignments': Assignment.objects.count(),
        'total_quizzes': Quiz.objects.count(),
        'pending_grades': pending_grades,
        'avg_gpa': round(
            AcademicRecord.objects.filter(total_credits_earned__gt=0).aggregate(avg=Avg('cumulative_gpa'))['avg'] or 0,
            2,
        ),
        'teachers': teachers,
        'recent_courses': recent_courses,
        'current_semester': current_semester,
    }
    return render(request, 'students/dashboard.html', context)


@student_required
def student_dashboard_view(request):
    """
    STUDENT Dashboard — personal academic data.

    RBAC: Only users with role='student' can access this.

    BUSINESS LOGIC:
        Shows the student's enrolled courses, GPA, upcoming assignments,
        and notifications. Data is scoped to the logged-in student only.
    """
    from apps.enrollments.models import CourseEnrollment
    from apps.assessments.models import Assignment
    from apps.communication.models import Notification

    student = None
    enrolled_courses = []
    gpa = 0.0
    total_credits = 0
    upcoming_assignments = []
    open_quizzes = []
    recent_materials = []
    notifications = []

    student = services.ensure_student_profile(request.user)

    if student:
        record = refresh_student_grades(student)
        enrolled_courses = CourseEnrollment.objects.filter(
            student=student, status='ENROLLED'
        ).select_related('course', 'course__subject', 'course__semester')[:10]
        gpa = record.cumulative_gpa
        total_credits = record.total_credits_earned

        # Upcoming assignments for enrolled courses
        enrolled_course_ids = CourseEnrollment.objects.filter(
            student=student, status='ENROLLED'
        ).values_list('course_id', flat=True)
        from django.utils import timezone
        upcoming_assignments = Assignment.objects.filter(
            course_id__in=enrolled_course_ids,
            due_date__gte=timezone.now()
        ).order_by('due_date')[:5]
        
        # Open Quizzes
        open_quizzes = Quiz.objects.filter(
            course_id__in=enrolled_course_ids,
            end_time__gte=timezone.now()
        ).exclude(
            id__in=QuizAttempt.objects.filter(student=student).values('quiz_id')
        ).order_by('end_time')[:5]
        
        # Recent Materials
        from apps.academics.models import CourseMaterial
        recent_materials = CourseMaterial.objects.filter(
            course_id__in=enrolled_course_ids
        ).select_related('course', 'course__subject')[:5]

    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]

    context = {
        'title': 'My Dashboard',
        'student': student,
        'enrolled_courses': enrolled_courses,
        'gpa': gpa,
        'total_credits': total_credits,
        'upcoming_assignments': upcoming_assignments,
        'open_quizzes': open_quizzes,
        'recent_materials': recent_materials,
        'notifications': notifications,
    }
    return render(request, 'students/student_dashboard.html', context)


@staff_required
def search_view(request):
    """
    Search functionality — STAFF only (Admin + Teacher).
    Students cannot search for other students.
    """
    form = StudentSearchForm(request.GET or None)
    results = None
    query = request.GET.get('query', '')

    if query:
        results = services.search_students(query)
        if hasattr(request.user, 'profile') and request.user.profile.is_teacher and results is not None:
            teacher_student_ids = CourseEnrollment.objects.filter(
                course__professor=request.user,
                status='ENROLLED',
            ).values_list('student_id', flat=True)
            results = results.filter(id__in=teacher_student_ids)
        if not results:
            messages.info(request, f'No students found matching "{query}".')

    context = {
        'title': 'Search Results',
        'form': form,
        'results': results,
        'query': query,
    }
    return render(request, 'students/search.html', context)


# =============================================================
# CRUD Operations — STAFF ONLY (Admin + Teacher)
# =============================================================

class StudentListView(StaffRequiredMixin, ListView):
    """List all students — Staff only."""
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'profile') and self.request.user.profile.is_teacher:
            teacher_student_ids = CourseEnrollment.objects.filter(
                course__professor=self.request.user,
                status='ENROLLED',
            ).values_list('student_id', flat=True)
            queryset = queryset.filter(id__in=teacher_student_ids).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Students' if self.request.user.profile.is_teacher else 'All Students'
        return context


class StudentDetailView(StaffRequiredMixin, DetailView):
    """
    View a student's profile.
    Staff can view any student.
    """
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'profile') and self.request.user.profile.is_teacher:
            teacher_student_ids = CourseEnrollment.objects.filter(
                course__professor=self.request.user,
                status='ENROLLED',
            ).values_list('student_id', flat=True)
            queryset = queryset.filter(id__in=teacher_student_ids).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Student Profile: {self.object.full_name}'
        return context


class StudentCreateView(AdminRequiredMixin, CreateView):
    """Add a new student — Staff only."""
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Student'
        context['button_text'] = 'Add Student'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Student added successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class StudentUpdateView(AdminRequiredMixin, UpdateView):
    """Edit a student — Staff only."""
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'

    def get_success_url(self):
        return reverse_lazy('students:student_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Student: {self.object.full_name}'
        context['button_text'] = 'Save Changes'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Student updated successfully!')
        return super().form_valid(form)


class StudentDeleteView(AdminRequiredMixin, DeleteView):
    """Delete a student — ADMIN only (not teachers)."""
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('students:student_list')
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Student: {self.object.full_name}'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Student deleted successfully!')
        return super().form_valid(form)


# =============================================================
# Custom Error Handlers
# =============================================================
def custom_404_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def custom_500_view(request):
    return render(request, 'errors/500.html', status=500)
