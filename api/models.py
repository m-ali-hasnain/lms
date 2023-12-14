import uuid

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
from django.core.exceptions import ValidationError
from .managers import CustomUserManager


class Course(models.Model):
    name = models.CharField(max_length=255, unique=True)
    credit_hours = models.IntegerField(default=3)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that inherits from AbstractBaseUser
    for custom functionality
    """

    ADMIN = 1
    STUDENT = 2

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (STUDENT, 'Student'),
    )

    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    email = models.EmailField(unique=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True, default=STUDENT)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    courses = models.ManyToManyField(Course, through='CourseRegistration', related_name='students')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_credit_hours(self):
        total_credit_hours = self.courses.aggregate(total_credit_hours=models.Sum('credit_hours')).get('total_credit_hours')
        return total_credit_hours or 0

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class CourseRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        user_credit_hours = self.user.get_credit_hours()
        if user_credit_hours + self.course.credit_hours > 30:
            raise ValidationError("Cannot exceed the maximum credit hours (30 hours).")
        super().save(*args, **kwargs)
