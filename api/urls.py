from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from .views import (
    UserRegistrationView,
    UserLoginView,
    UserListView,
    CourseListView,
    CourseDetailsView,
    CourseRegistrationDetailsView,
    CourseRegistrationView
)

urlpatterns = [
    path('token/obtain', jwt_views.TokenObtainPairView.as_view(), name='token_create'),
    path('token/refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('users/register', UserRegistrationView.as_view(), name='register'),
    path('users/login', UserLoginView.as_view(), name='login'),
    path('users', UserListView.as_view(), name='users'),
    path('courses', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>', CourseDetailsView.as_view(), name='course-detail'),
    path('register/courses', CourseRegistrationView.as_view(), name='registered-courses-list'),
    path('registered/courses/<int:pk>', CourseRegistrationDetailsView.as_view(), name='registered-course-detail')
]