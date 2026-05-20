from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import Course, CourseMaterial, Semester, Subject, SubjectBook, Timetable


class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['name', 'term', 'year', 'start_date', 'end_date', 'is_current']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['code', 'title', 'description', 'credits', 'department']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'credits': forms.NumberInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['subject', 'semester', 'professor', 'capacity']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'professor': forms.Select(attrs={'class': 'form-select'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['professor'].queryset = User.objects.filter(profile__role='teacher').order_by('username')


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['course', 'day_of_week', 'start_time', 'end_time', 'room_number']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['title', 'description', 'file_attachment', 'url_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Week 1 Lecture Notes'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file_attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'url_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        file_attachment = cleaned_data.get('file_attachment')
        url_link = cleaned_data.get('url_link')
        if not file_attachment and not url_link:
            raise ValidationError('Upload a file or provide a resource link.')
        return cleaned_data


class SubjectBookForm(forms.ModelForm):
    """
    Form for teachers to upload books/documents linked to a Subject.
    Enforces file type validation (PDF, DOC, DOCX) and max file size of 10MB.
    """
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    class Meta:
        model = SubjectBook
        fields = ['title', 'description', 'file_attachment']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Introduction to Algorithms',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of this material...',
            }),
            'file_attachment': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
            }),
        }

    def clean_file_attachment(self):
        file = self.cleaned_data.get('file_attachment')
        if file:
            if file.size > self.MAX_FILE_SIZE:
                raise ValidationError(
                    f'File too large. Maximum size is {self.MAX_FILE_SIZE // (1024 * 1024)}MB.'
                )
        return file
