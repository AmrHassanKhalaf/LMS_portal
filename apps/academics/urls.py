from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    # Existing Routes
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('admin-academics/', views.admin_academics_panel, name='admin_academics_panel'),
    path('admin-academics/semesters/add/', views.admin_semester_form, name='admin_semester_add'),
    path('admin-academics/semesters/<int:semester_id>/edit/', views.admin_semester_form, name='admin_semester_edit'),
    path('admin-academics/subjects/add/', views.admin_subject_form, name='admin_subject_add'),
    path('admin-academics/subjects/<int:subject_id>/edit/', views.admin_subject_form, name='admin_subject_edit'),
    path('admin-academics/courses/add/', views.admin_course_form, name='admin_course_add'),
    path('admin-academics/courses/<int:course_id>/edit/', views.admin_course_form, name='admin_course_edit'),
    path('admin-academics/timetable/add/', views.admin_timetable_form, name='admin_timetable_add'),
    path('admin-academics/timetable/<int:timetable_id>/edit/', views.admin_timetable_form, name='admin_timetable_edit'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher-dashboard/weak-students/<int:enrollment_id>/add/', views.flag_weak_student, name='flag_weak_student'),
    path('teacher-dashboard/weak-students/<int:enrollment_id>/remove/', views.unflag_weak_student, name='unflag_weak_student'),
    path('semesters/', views.semester_list, name='semester_list'),
    path('courses/', views.course_list, name='course_list'),
    path('materials/', views.material_overview, name='material_overview'),
    path('courses/<int:course_id>/materials/', views.course_material_list, name='course_material_list'),
    path('courses/<int:course_id>/materials/upload/', views.upload_course_material, name='upload_course_material'),
    path('timetable/', views.timetable_view, name='timetable_view'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('notifications/', views.notification_list, name='notification_list'),

    # NEW: Subject Browsing & Curriculum
    path('subjects/', views.browse_subjects, name='browse_subjects'),
    path('subjects/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('subjects/<int:subject_id>/add/', views.add_to_curriculum, name='add_to_curriculum'),
    path('subjects/<int:subject_id>/remove/', views.remove_from_curriculum, name='remove_from_curriculum'),
    path('my-curriculum/', views.my_curriculum, name='my_curriculum'),

    # NEW: Teacher Book Management
    path('subjects/<int:subject_id>/upload-book/', views.upload_subject_book, name='upload_subject_book'),
    path('books/<int:book_id>/delete/', views.delete_subject_book, name='delete_subject_book'),

    # NEW: Teacher Quiz Management
    path('subjects/<int:subject_id>/create-quiz/', views.create_subject_quiz, name='create_subject_quiz'),
    path('subject-quiz/<int:quiz_id>/manage/', views.manage_subject_quiz, name='manage_subject_quiz'),
    path('subject-quiz/<int:quiz_id>/delete/', views.delete_subject_quiz, name='delete_subject_quiz'),
    path('subject-quiz/<int:quiz_id>/results/', views.subject_quiz_results, name='subject_quiz_results'),

    # NEW: Student Quiz Taking
    path('subject-quiz/<int:quiz_id>/take/', views.take_subject_quiz, name='take_subject_quiz'),
]
