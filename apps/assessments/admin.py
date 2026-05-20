from django.contrib import admin
from .models import (
    Assignment,
    Choice,
    Question,
    Quiz,
    QuizAttempt,
    SubjectChoice,
    SubjectQuestion,
    SubjectQuiz,
    SubjectQuizAttempt,
    Submission,
)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class SubjectChoiceInline(admin.TabularInline):
    model = SubjectChoice
    extra = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3


class SubjectQuestionInline(admin.TabularInline):
    model = SubjectQuestion
    extra = 3


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'assignment_type', 'due_date', 'max_score')
    list_filter = ('assignment_type', 'due_date', 'course__semester')
    search_fields = ('title', 'course__subject__code')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'score', 'is_late')
    list_filter = ('assignment__course', 'submitted_at')
    search_fields = ('student__first_name', 'student__last_name')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'start_time', 'end_time', 'time_limit_minutes')
    list_filter = ('course__semester', 'start_time')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'question_type', 'points')
    list_filter = ('question_type', 'quiz')
    inlines = [ChoiceInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'start_time', 'end_time', 'score')
    list_filter = ('quiz',)


@admin.register(SubjectQuiz)
class SubjectQuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'num_questions', 'total_marks', 'passing_score', 'created_at')
    list_filter = ('subject__department', 'created_at')
    search_fields = ('title', 'subject__code', 'subject__title')
    inlines = [SubjectQuestionInline]


@admin.register(SubjectQuestion)
class SubjectQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'question_type', 'points')
    list_filter = ('question_type', 'quiz')
    inlines = [SubjectChoiceInline]


@admin.register(SubjectQuizAttempt)
class SubjectQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'start_time', 'end_time', 'score')
    list_filter = ('quiz',)
    search_fields = ('student__admission_number', 'student__first_name', 'student__last_name', 'quiz__title')
