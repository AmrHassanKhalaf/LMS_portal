from django.contrib import admin
from .models import CourseEnrollment, AcademicRecord

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'overall_score', 'final_grade', 'is_flagged_weak', 'enrollment_date')
    list_filter = ('status', 'final_grade', 'is_flagged_weak', 'course__semester')
    search_fields = ('student__first_name', 'student__last_name', 'student__admission_number', 'course__subject__code')

@admin.register(AcademicRecord)
class AcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'cumulative_gpa', 'total_credits_earned')
    search_fields = ('student__first_name', 'student__last_name', 'student__admission_number')
    readonly_fields = ('cumulative_gpa', 'total_credits_earned')
