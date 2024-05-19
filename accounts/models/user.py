from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as gtl


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(gtl("Ingresa un correo válido"))

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(gtl("El superusuario debe tener is_staff = True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(gtl("El superusuario debe tener is_superuser = True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.BigAutoField(
        auto_created=True, primary_key=True, serialize=False, editable=False
    )
    email = models.EmailField(blank=False, unique=True, max_length=255)
    phone = models.CharField(blank=False, unique=True, max_length=20)
    first_name = models.CharField(blank=False, max_length=50)
    last_name = models.CharField(blank=False, max_length=50)
    gender = models.CharField(blank=True, max_length=1)
    is_active = models.BooleanField(default=False)
    verification_code = models.CharField(blank=True, null=True, max_length=6)

    total_stars_driver = models.IntegerField(default=0)
    total_trips_driver = models.IntegerField(default=0)
    rating_driver = models.FloatField(default=0)
    currently_driver = models.BooleanField(default=False)
    current_trip_driver = models.ForeignKey(
        "core.Trip",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="driver",
    )

    total_stars_passenger = models.IntegerField(default=0)
    total_trips_passenger = models.IntegerField(default=0)
    rating_passenger = models.FloatField(default=0)
    currently_passenger = models.BooleanField(default=False)
    current_offer_passenger = models.ForeignKey(
        "core.Offer",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="passenger",
    )

    # Remove username field and set email as the USERNAME_FIELD
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()

    def verify(self, code):
        if self.verification_code != code:
            return False

        self.is_active = True
        self.verification_code = None
        self.save()

        return True

    def has_active_trip(self):
        return self.currently_driver or self.currently_passenger

    def get_active_trip(self):
        if self.currently_driver:
            return self.current_trip_driver
        elif self.currently_passenger:
            return self.current_offer_passenger.trip

    def start_as_driver(self, trip):
        self.currently_passenger = False
        self.current_offer_passenger = None
        self.currently_driver = True
        self.current_trip_driver = trip
        self.save()

    def start_as_passenger(self, offer):
        self.currently_driver = False
        self.current_trip_driver = None
        self.currently_passenger = True
        self.current_offer_passenger = offer
        self.save()

    def rate_as_driver(self, stars):
        if not self.currently_driver:
            raise ValueError("El usuario no es un conductor ahora mismo.")

        self.total_stars_driver += stars
        self.total_trips_driver += 1
        self.rating_driver = self.total_stars_driver / self.total_trips_driver
        self.save()

    def rate_as_passenger(self, stars):
        if not self.currently_passenger:
            raise ValueError("El usuario no es un pasajero ahora mismo.")

        self.total_stars_passenger += stars
        self.total_trips_passenger += 1
        self.rating_passenger = self.total_stars_passenger / self.total_trips_passenger
        self.save()

    def finish_trip(self):
        if not self.currently_driver and not self.current_trip_driver:
            raise ValueError("Este usuario no es un conductor ni pasajero ahora mismo.")

        if self.currently_driver:
            self.currently_driver = False
            self.current_trip_driver = None

        elif self.currently_passenger:
            self.currently_passenger = False
            self.current_offer_passenger = None

    def __str__(self):
        return self.get_full_name()
