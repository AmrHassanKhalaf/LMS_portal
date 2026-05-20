from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    # Teacher: Assignment Management
    path('assignments/manage/', views.manage_assignments, name='manage_assignments'),
    path('assignments/create/', views.create_assignment, name='create_assignment'),
    path('assignments/<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('assignments/<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),

    # Teacher: Gradebook
    path('gradebook/', views.gradebook_courses, name='gradebook_courses'),
    path('gradebook/course/<int:course_id>/', views.gradebook_students, name='gradebook_students'),
    path('gradebook/course/<int:course_id>/student/<int:student_id>/', views.gradebook_student_detail, name='gradebook_student_detail'),
    path('gradebook/submission/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    
    # Teacher: Quiz Management
    path('quizzes/manage/', views.manage_quizzes, name='manage_quizzes'),
    path('quizzes/create/', views.create_quiz, name='create_quiz'),
    path('quizzes/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quizzes/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('quizzes/<int:quiz_id>/questions/', views.quiz_questions, name='quiz_questions'),
    path('questions/<int:question_id>/choices/add/', views.add_choice, name='add_choice'),

    # Student: Transcripts & Quizzes
    path('my-transcript/', views.my_transcript, name='my_transcript'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('quizzes/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
]
