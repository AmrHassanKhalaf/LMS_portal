from rest_framework import serializers
from apps.students.models import Student
from apps.academics.models import Course, Subject, Semester
from apps.enrollments.models import CourseEnrollment

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    semester = SemesterSerializer(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = '__all__'
