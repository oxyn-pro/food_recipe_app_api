from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# BaseUserManager class - in order to create our own custom user manager
# AbstractBaseUser class - in order to create our own custom user model
from django.contrib.auth.models import PermissionsMixin
# PermissionsMixin - to manage and create custom permissions for a user


class CustomUserManager(BaseUserManager):
    """Helps to create user(s), and to create super user(s) and etc."""
    def create_user(self, email, password=None, **extra_fields):
        """Creates a new user"""
        if not email:
            raise ValueError("User must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Creates and saves a new superuser"""
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Customer User Model that supports "email" to be instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
