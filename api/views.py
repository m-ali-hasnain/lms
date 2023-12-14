from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from django.core.exceptions import ValidationError

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserListSerializer,
    CourseSerializer,
    CourseRegistrationSerializer
)

from .models import User, Course, CourseRegistration
from .permissions import AdminPermission, StudentPermission


class UserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            serializer.save()
            status_code = status.HTTP_201_CREATED

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'User successfully registered!',
                'user': serializer.data
            }

            return Response(response, status=status_code)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            status_code = status.HTTP_200_OK
            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'User logged in successfully',
                'access': serializer.data['access'],
                'refresh': serializer.data['refresh'],
                'authenticatedUser': {
                    'email': serializer.data['email'],
                    'role': serializer.data['role']
                }
            }

            return Response(response, status=status_code)


class UserListView(APIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated, AdminPermission)

    def get(self, request):
        users = User.objects.all()
        serializer = self.serializer_class(users, many=True)
        response = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully fetched users',
            'users': serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)


class CourseListView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated, AdminPermission)

    def list(self, request, *args, **kwargs):
        courses = Course.objects.all()
        serializer = self.serializer_class(courses, many=True)
        response_data = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Successfully fetched courses',
            'courses': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                'success': True,
                'status_code': status.HTTP_201_CREATED,
                'message': 'Course successfully created',
                'course': serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response_data = {
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid data for course creation',
                'errors': serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class CourseDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = (IsAuthenticated, AdminPermission,)


class CourseRegistrationView(generics.ListCreateAPIView):
    serializer_class = CourseRegistrationSerializer
    permission_classes = [IsAuthenticated, StudentPermission]

    def get_queryset(self):
        return CourseRegistration.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            response_data = self.validate_user(request.user, serializer.validated_data['user'])
            if response_data:
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            response_data = self.validate_credit_hours(request.user, serializer.validated_data['course'])
            if response_data:
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(user=request.user)
            response_data = {
                'success': True,
                'status_code': status.HTTP_201_CREATED,
                'message': 'Course registered successfully',
                'registered_course': serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response_data = {
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'Validation Error',
                'errors': serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def validate_user(self, requesting_user, target_user):
        if requesting_user != target_user:
            return {
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'Validation Error',
                'errors': {'course_registration': ['You can only register for courses on your behalf.']}
            }
        return None

    def validate_credit_hours(self, user, course):
        user_credit_hours = user.get_credit_hours()
        course_credit_hours = course.credit_hours

        if user_credit_hours + course_credit_hours > 30:
            return {
                'success': False,
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'Validation Error',
                'errors': {'credit_hours': ['Exceeds maximum credit hours.']}
            }
        return None


class CourseRegistrationDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseRegistrationSerializer
    permission_classes = (IsAuthenticated, StudentPermission,)

    def get_queryset(self):
        return CourseRegistration.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        user_credit_hours = instance.user.get_credit_hours()
        if user_credit_hours - instance.course.credit_hours < 0:
            raise ValidationError("Cannot have negative credit hours.")
        super().perform_destroy(instance)
