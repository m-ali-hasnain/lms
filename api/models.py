import uuid

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):

    """
    Custom User model that inherits from AbstractBaseUser
    for custom functionality
    """

    # Roles, users can have
    ADMIN = 1
    STUDENT = 2

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (STUDENT, 'Student'),
    )

    # Fields definitions
    
    # identifier to use safely in urls
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    
    # registering other user fields
    email = models.EmailField(unique=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True, default=2) # Default to Student
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True) 
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager() # manager for User

    def __str__(self):
        """
        Represents instance of User model
        """
        return self.email
  
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'