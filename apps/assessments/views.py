"""
Assessments Views — Grading, Quizzes, and Transcripts
======================================================
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from apps.accounts.decorators import teacher_required, student_required
from apps.academics.models import Course
from apps.enrollments.models import CourseEnrollment
from apps.enrollments.services import refresh_course_grades, refresh_student_grades
from apps.students.models import Student
from apps.students.services import ensure_student_profile
from .models import Assignment, Submission, Quiz, Question, Choice, QuizAttempt, SubjectQuizAttempt
from .forms import AssignmentForm, GradeSubmissionForm, QuizForm, QuestionForm, ChoiceForm, SubmissionForm


# =========================================================
# TEACHER: ASSIGNMENT MANAGEMENT
# =========================================================

@teacher_required
def manage_assignments(request):
    """List assignments managed by this teacher."""
    assignments = Assignment.objects.filter(
        course__professor=request.user
    ).select_related('course', 'course__subject').order_by('-created_at')
    return render(request, 'assessments/manage_assignments.html', {'assignments': assignments})


@teacher_required
def create_assignment(request):
    """Create a new assignment for one of the teacher's courses."""
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
    else:
        form = AssignmentForm()

    form.fields['course'].queryset = Course.objects.filter(professor=request.user)

    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        if assignment.course.professor != request.user:
            return render(request, 'errors/403.html', status=403)
        assignment.save()
        messages.success(request, 'Assignment created successfully.')
        return redirect('assessments:manage_assignments')

    return render(request, 'assessments/assignment_form.html', {
        'form': form,
        'title': 'Create Assignment',
    })


@teacher_required
def edit_assignment(request, assignment_id):
    """Edit an assignment owned by this teacher."""
    assignment = get_object_or_404(Assignment, id=assignment_id, course__professor=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
    else:
        form = AssignmentForm(instance=assignment)

    form.fields['course'].queryset = Course.objects.filter(professor=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Assignment updated successfully.')
        return redirect('assessments:manage_assignments')

    return render(request, 'assessments/assignment_form.html', {
        'form': form,
        'title': f'Edit Assignment: {assignment.title}',
    })


@teacher_required
def delete_assignment(request, assignment_id):
    """Delete an assignment owned by this teacher."""
    assignment = get_object_or_404(Assignment, id=assignment_id, course__professor=request.user)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully.')
        return redirect('assessments:manage_assignments')
    return render(request, 'assessments/assignment_confirm_delete.html', {'assignment': assignment})


# =========================================================
# TEACHER: GRADEBOOK
# =========================================================

@teacher_required
def gradebook_courses(request):
    """List courses taught by this teacher for grading."""
    courses = Course.objects.filter(professor=request.user).select_related('subject', 'semester')
    return render(request, 'assessments/gradebook_courses.html', {'courses': courses})


@teacher_required
def gradebook_students(request, course_id):
    """List all enrolled students in a specific course."""
    course = get_object_or_404(Course, id=course_id, professor=request.user)
    enrollments = CourseEnrollment.objects.filter(
        course=course,
        status__in=['ENROLLED', 'COMPLETED'],
    ).select_related('student')
    
    # Pre-calculate overall scores to ensure they are up-to-date.
    refresh_course_grades(course)
    enrollments = CourseEnrollment.objects.filter(
        course=course,
        status__in=['ENROLLED', 'COMPLETED'],
    ).select_related('student')
        
    return render(request, 'assessments/gradebook_students.html', {
        'course': course, 
        'enrollments': enrollments
    })


@teacher_required
def gradebook_student_detail(request, course_id, student_id):
    """View a specific student's assignments and quizzes for a course."""
    course = get_object_or_404(Course, id=course_id, professor=request.user)
    student = get_object_or_404(Student, id=student_id)
    enrollment = get_object_or_404(CourseEnrollment, course=course, student=student)
    enrollment.compute_overall_score()
    enrollment.refresh_from_db()
    
    submissions = Submission.objects.filter(
        student=student, assignment__course=course
    ).select_related('assignment')
    
    quiz_attempts = QuizAttempt.objects.filter(
        student=student, quiz__course=course
    ).select_related('quiz')

    subject_quiz_attempts = SubjectQuizAttempt.objects.filter(
        student=student,
        quiz__subject=course.subject,
    ).select_related('quiz')
    
    return render(request, 'assessments/gradebook_student_detail.html', {
        'course': course,
        'student': student,
        'enrollment': enrollment,
        'submissions': submissions,
        'quiz_attempts': quiz_attempts,
        'subject_quiz_attempts': subject_quiz_attempts,
    })


@teacher_required
def grade_submission(request, submission_id):
    """Interface to assign a score and feedback to an assignment submission."""
    submission = get_object_or_404(Submission, id=submission_id)
    
    # RBAC: Only the professor of the course can grade it
    if submission.assignment.course.professor != request.user:
        return render(request, 'errors/403.html', status=403)
        
    if request.method == 'POST':
        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            # Trigger overall score recalculation
            enrollment = CourseEnrollment.objects.filter(
                student=submission.student, course=submission.assignment.course
            ).first()
            if enrollment:
                enrollment.compute_overall_score()
                
            messages.success(request, f'Grade saved for {submission.student.full_name}')
            return redirect('assessments:gradebook_student_detail', 
                            course_id=submission.assignment.course.id, 
                            student_id=submission.student.id)
    else:
        form = GradeSubmissionForm(instance=submission)
        
    return render(request, 'assessments/grade_submission.html', {
        'submission': submission, 
        'form': form
    })

# =========================================================
# TEACHER: QUIZ MANAGEMENT
# =========================================================

@teacher_required
def manage_quizzes(request):
    """List quizzes managed by this teacher."""
    quizzes = Quiz.objects.filter(course__professor=request.user).select_related('course')
    return render(request, 'assessments/manage_quizzes.html', {'quizzes': quizzes})


@teacher_required
def create_quiz(request):
    """Create a new quiz."""
    if request.method == 'POST':
        form = QuizForm(request.POST)
    else:
        form = QuizForm()

    # Filter courses to only those taught by this teacher.
    form.fields['course'].queryset = Course.objects.filter(professor=request.user)

    if request.method == 'POST' and form.is_valid():
        quiz = form.save(commit=False)
        if quiz.course.professor != request.user:
            return render(request, 'errors/403.html', status=403)
        quiz.save()
        messages.success(request, 'Quiz created successfully. Now add questions.')
        return redirect('assessments:quiz_questions', quiz_id=quiz.id)

    return render(request, 'assessments/quiz_form.html', {'form': form, 'title': 'Create Quiz'})


@teacher_required
def edit_quiz(request, quiz_id):
    """Edit an existing quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id, course__professor=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
    else:
        form = QuizForm(instance=quiz)

    form.fields['course'].queryset = Course.objects.filter(professor=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Quiz updated successfully.')
        return redirect('assessments:manage_quizzes')

    return render(request, 'assessments/quiz_form.html', {'form': form, 'title': f'Edit Quiz: {quiz.title}'})


@teacher_required
def delete_quiz(request, quiz_id):
    """Delete a quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id, course__professor=request.user)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully.')
        return redirect('assessments:manage_quizzes')
    return render(request, 'assessments/quiz_confirm_delete.html', {'quiz': quiz})


@teacher_required
def quiz_questions(request, quiz_id):
    """Manage questions and choices for a quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id, course__professor=request.user)
    questions = Question.objects.filter(quiz=quiz).prefetch_related('choices')
    
    if request.method == 'POST' and 'add_question' in request.POST:
        q_form = QuestionForm(request.POST)
        if q_form.is_valid():
            question = q_form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added.')
            return redirect('assessments:quiz_questions', quiz_id=quiz.id)
    else:
        q_form = QuestionForm()
        
    return render(request, 'assessments/quiz_questions.html', {
        'quiz': quiz,
        'questions': questions,
        'q_form': q_form
    })


@teacher_required
def add_choice(request, question_id):
    """Add a choice to a question (AJAX or standard POST)."""
    question = get_object_or_404(Question, id=question_id, quiz__course__professor=request.user)
    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            messages.success(request, 'Choice added.')
    return redirect('assessments:quiz_questions', quiz_id=question.quiz.id)

# =========================================================
# STUDENT: TRANSCRIPTS & GRADES
# =========================================================

@student_required
def my_transcript(request):
    """View overall letter grades and GPA."""
    student = ensure_student_profile(request.user)
    academic_record = refresh_student_grades(student)
    enrollments = CourseEnrollment.objects.filter(
        student=student,
        status__in=['ENROLLED', 'COMPLETED'],
    ).select_related('course', 'course__subject', 'course__semester')
    
    return render(request, 'assessments/my_transcript.html', {
        'student': student,
        'academic_record': academic_record,
        'enrollments': enrollments
    })


@student_required
def submit_assignment(request, assignment_id):
    """Allow an enrolled student to submit an assignment once."""
    assignment = get_object_or_404(Assignment.objects.select_related('course'), id=assignment_id)
    student = ensure_student_profile(request.user)

    is_enrolled = CourseEnrollment.objects.filter(
        student=student,
        course=assignment.course,
        status='ENROLLED',
    ).exists()
    if not is_enrolled:
        return render(request, 'errors/403.html', status=403)

    existing_submission = Submission.objects.filter(assignment=assignment, student=student).first()
    if existing_submission:
        messages.info(request, 'You have already submitted this assignment.')
        return redirect('academics:assignment_list')

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = student
            submission.save()
            messages.success(request, 'Assignment submitted successfully.')
            return redirect('academics:assignment_list')
    else:
        form = SubmissionForm()

    return render(request, 'assessments/submit_assignment.html', {
        'assignment': assignment,
        'form': form,
    })


@student_required
def take_quiz(request, quiz_id):
    """Interactive quiz view for students with auto-grading."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = ensure_student_profile(request.user)
    
    # RBAC: Verify student is enrolled in the course
    is_enrolled = CourseEnrollment.objects.filter(student=student, course=quiz.course, status='ENROLLED').exists()
    if not is_enrolled:
        return render(request, 'errors/403.html', status=403)
        
    # Check if student already took this quiz
    if QuizAttempt.objects.filter(student=student, quiz=quiz).exists():
        messages.info(request, "You have already completed this quiz.")
        return redirect('assessments:my_transcript')
        
    questions = Question.objects.filter(quiz=quiz).prefetch_related('choices')
    
    if request.method == 'POST':
        from django.utils import timezone
        
        # Auto-grade logic
        score = 0.0
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                try:
                    choice = Choice.objects.get(id=selected_choice_id, question=question)
                    if choice.is_correct:
                        score += float(question.points)
                except Choice.DoesNotExist:
                    pass
                    
        # Scale score to quiz.total_marks based on points earned vs total possible points
        total_possible_points = sum([float(q.points) for q in questions])
        if total_possible_points > 0:
            final_score = (score / total_possible_points) * float(quiz.total_marks)
        else:
            final_score = float(quiz.total_marks) # If quiz has no points defined but questions exist, give full marks
            
        # Create attempt record
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=student,
            end_time=timezone.now(),
            score=round(final_score, 2)
        )
        
        # Trigger recalculation of the overall score in the course enrollment
        enrollment = CourseEnrollment.objects.get(student=student, course=quiz.course)
        enrollment.compute_overall_score()
        
        messages.success(request, f"Quiz submitted! Your score: {attempt.score} / {quiz.total_marks}")
        return redirect('assessments:my_transcript')
        
    return render(request, 'assessments/take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })
