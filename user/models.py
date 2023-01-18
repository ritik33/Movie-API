from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from rest_framework_simplejwt.tokens import RefreshToken


#  Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, password2=None):
        """
        Creates and saves a User with the given email, username and password.
        """
        if not email:
            raise ValueError("User must have a valid email address")

        if not username:
            raise ValueError("User must have a valid username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password=None):
        """
        Creates and saves a superuser with the given email, username and password.
        """
        user = self.create_user(
            email,
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_verified = True
        user.is_superuser = True
        user.save()
        return user


#  Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        # "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        # "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        # "Is the user a member of staff?"
        return self.is_admin

    def tokens(self):
        token = RefreshToken.for_user(self)
        return {"refresh": str(token), "access": str(token.access_token)}
