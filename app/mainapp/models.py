from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# BaseUserManager class - in order to create our own custom user manager
# AbstractBaseUser class - in order to create our own custom user model
from django.contrib.auth.models import PermissionsMixin
# PermissionsMixin - to manage and create custom permissions for a user

from django.conf import settings  # importing settings from core 'app' app


class CustomUserManager(BaseUserManager):
    """Helps to create user(s), and to create super user(s) and etc."""
    def create_user(self, email, password=None, **extra_fields):
        """Creates a new user"""
        if not email:
            raise ValueError("User must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        # here self.model() referes back to the class it manages for,
        # (ie. CustomUserManager manages CustomUser), then self.model()
        # is called in 'create_user' then it will put attributes of
        # CustomUser as parameters self.model(**params). It can be also
        # understood as CustomUser(email=self.normalize_email(email), and etc)
        user.set_password(password)  # set_password func comes with
        # AbstractBaseUser
        user.save(self._db)

        return user

    # here in create_superuser we can use create_user func that we created
    def create_superuser(self, email, password=None, **extra_fields):
        """Creates and saves a new superuser"""
        if not email:
            raise ValueError("User must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


# it should originally be overridden as User but that's why preferred -
class CustomUser(AbstractBaseUser, PermissionsMixin):  # to put CustomUser
    """Customer User Model that supports "email" to be instead of username,
       with other words, this is database model for users in the system.
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"


class Tag(models.Model):
    """Tag in order to use in 'recipe'"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """Returns string representation"""
        return self.name


class Ingredient(models.Model):
    """Ingredient in order to use in 'recipe'"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """Returns string representation"""
        return self.name


class Recipe(models.Model):
    """Recipe object/table"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255, null=False)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    # blank is recommended than null, because in null blank should also
    # be checked, which makes code makes process a bit complicated

    ingredients = models.ManyToManyField('Ingredient')
    # if you put Ingredient without quotes, then you need to have correct
    # order of classes, meaning that Ingredient must come before Recipe.
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title
