from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.students.models import Student
from apps.academics.models import Course
from apps.enrollments.models import CourseEnrollment
from .serializers import StudentSerializer, CourseSerializer, CourseEnrollmentSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

class CourseEnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CourseEnrollment.objects.all()
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [IsAuthenticated]
