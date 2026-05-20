"""
Students URL Configuration
============================

WHY THIS FILE EXISTS:
    Maps URL paths to their corresponding views in the students app.
    Keeps routing localized to the app.

URL PATTERNS:
    /students/              → Dashboard (home)
    /students/list/         → List all students
    /students/search/       → Search results
    /students/add/          → Create new student
    /students/<pk>/         → View student details
    /students/<pk>/edit/    → Update student
    /students/<pk>/delete/  → Delete student
"""

from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Dashboard and Search (Function-Based Views)
    path('', views.dashboard_view, name='dashboard'),
    path('my-dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('search/', views.search_view, name='search'),

    # CRUD Operations (Class-Based Views)
    path('list/', views.StudentListView.as_view(), name='student_list'),
    path('add/', views.StudentCreateView.as_view(), name='student_create'),
    
    # <int:pk> captures the student's ID from the URL and passes it to the view
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_update'),
    path('<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
]
