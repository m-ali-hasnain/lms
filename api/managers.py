from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Manager class for creating users and superusers
    It also does validation stuff on email and password fields
    """
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The email field is required."))
        if not password:
            raise ValueError(_("The password field is required."))
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 1) # Super user default role is Admin

        if extra_fields.get('role') != 1:
            raise ValueError('Superuser must have role of Admin')
        return self.create_user(email, password, **extra_fields)