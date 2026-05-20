"""
Student Forms
==============

WHY THIS FILE EXISTS:
    Forms are the bridge between user input and the database.
    ModelForm auto-generates form fields from model fields, keeping
    code DRY (Don't Repeat Yourself).

HOW IT CONNECTS:
    views.py creates form instances → templates render them →
    user submits → views.py validates → model saves to DB

DESIGN DECISIONS:
    1. ModelForm generates fields from the Student model automatically
    2. We customize widgets to add Bootstrap classes and placeholders
    3. clean_ methods provide field-level validation
    4. The image field uses FileInput (not ClearableFileInput) for a
       cleaner look — the template handles the clear checkbox separately.
"""

from django import forms
from django.utils import timezone

from .models import Student


class StudentForm(forms.ModelForm):
    """
    Form for creating and editing students.

    IMPORTANT:
        This form is used for BOTH create and update operations.
        The view determines which by passing an existing instance.

    FIELD CUSTOMIZATION:
        We override widgets to add Bootstrap classes and HTML5
        attributes for a polished user experience.
    """

    class Meta:
        model = Student
        fields = [
            'admission_number',
            'first_name',
            'last_name',
            'email',
            'date_of_birth',
            'gender',
            'phone_number',
            'address',
            'academic_level',
            'enrollment_date',
            'status',
            'image',
        ]
        widgets = {
            'admission_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., STU001',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'student@example.com',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',  # HTML5 date picker
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full address',
            }),
            'academic_level': forms.Select(attrs={
                'class': 'form-select',
            }),
            'enrollment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',  # Browser-level filter
            }),
        }

    def clean_admission_number(self):
        """
        Validate admission number format.

        Strips whitespace and converts to uppercase for consistency.
        This prevents 'stu001' and 'STU001' from being different records.
        """
        admission_number = self.cleaned_data.get('admission_number', '').strip().upper()
        if not admission_number:
            raise forms.ValidationError('Admission number is required.')
        return admission_number

    def clean_date_of_birth(self):
        """
        Ensure date of birth is not in the future.

        COMMON MISTAKE:
            Not validating dates on the backend. Frontend validation
            alone is easily bypassed — always validate server-side too.
        """
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth and date_of_birth > timezone.now().date():
            raise forms.ValidationError('Date of birth cannot be in the future.')
        return date_of_birth

    def clean_enrollment_date(self):
        """Ensure enrollment date is not in the future."""
        enrollment_date = self.cleaned_data.get('enrollment_date')
        if enrollment_date and enrollment_date > timezone.now().date():
            raise forms.ValidationError('Enrollment date cannot be in the future.')
        return enrollment_date


class StudentSearchForm(forms.Form):
    """
    Simple search form — not tied to any model.

    WHY a separate form?
        Search is a query operation, not a CRUD operation.
        It doesn't create or modify data, so a plain Form
        (not ModelForm) is appropriate.
    """
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name or admission number...',
            'aria-label': 'Search students',
        }),
    )
