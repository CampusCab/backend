from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as gtl

class UserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email: raise ValueError(gtl("The email must be set"))

        user = self.model(email = email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True: raise ValueError(gtl("Superuser must have is_staff = True."))
        if extra_fields.get("is_superuser") is not True: raise ValueError(gtl("Superuser must have is_superuser = True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):

    id = models.BigAutoField(
        primary_key = True,
        auto_created = True,
        serialize = False,
        verbose_name = "ID",
        editable = False,
    )

    email = models.EmailField(
        blank = False,
        unique = True,
        max_length = 255,
    )

    phone = models.CharField(
        blank = False,
        unique = True,
        max_length = 20,
    )

    first_name = models.CharField(
        blank = False,
        max_length = 50,
    )

    last_name = models.CharField(
        blank = False,
        max_length = 50,
    )

    is_active = models.BooleanField(
        default = False
    )

    verification_code = models.CharField(
        blank = True,
        null = True,
        max_length = 6
    )


    # Remove username field and set email as the USERNAME_FIELD
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()


    def verify(self, code):
        if self.verification_code != code: return False

        self.is_active = True
        self.verification_code = None
        self.save()

        return True


    def __str__(self):
        return self.get_full_name()
