from django.contrib import admin
from .models import CourseMaterial, Semester, Subject, SubjectBook, StudentCurriculum, Course, Timetable

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'term', 'year', 'start_date', 'end_date', 'is_current')
    list_filter = ('term', 'year', 'is_current')
    search_fields = ('name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'credits', 'department')
    list_filter = ('department', 'credits')
    search_fields = ('code', 'title')

class TimetableInline(admin.TabularInline):
    model = Timetable
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('subject', 'semester', 'professor', 'capacity', 'enrolled_count')
    list_filter = ('semester', 'subject__department', 'professor')
    search_fields = ('subject__code', 'subject__title', 'professor__username')
    inlines = [TimetableInline]

    def enrolled_count(self, obj):
        return obj.enrollments.filter(status='ENROLLED').count()


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('course', 'day_of_week', 'start_time', 'end_time', 'room_number')
    list_filter = ('day_of_week', 'course__semester')
    search_fields = ('course__subject__code', 'course__subject__title', 'room_number')


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    list_filter = ('course__semester', 'course__professor')
    search_fields = ('title', 'description', 'course__subject__code')


@admin.register(SubjectBook)
class SubjectBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'uploaded_at')
    list_filter = ('subject__department',)
    search_fields = ('title', 'subject__code', 'subject__title')


@admin.register(StudentCurriculum)
class StudentCurriculumAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'added_at')
    list_filter = ('subject__department',)
    search_fields = ('student__admission_number', 'student__first_name', 'student__last_name', 'subject__code')
