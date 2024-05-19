from django.db import models

from accounts.models import User
from .trip import Trip


class Offer(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    amount = models.IntegerField()
    accepted = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    stars_to_user = models.IntegerField(null=True, blank=True)
    stars_to_driver = models.IntegerField(null=True, blank=True)

    def clean(self):
        if self.amount <= 0:
            raise ValueError("El monto debe ser mayor o igual a cero.")

    def accept(self):
        if self.accepted:
            raise ValueError("La oferta ya ha sido aceptada.")
        if self.finished:
            raise ValueError("La oferta ya ha sido finalizada.")

        self.accepted = True
        self.save()

    def reject(self):
        if self.accepted:
            raise ValueError("La oferta ya ha sido aceptada.")
        if self.finished:
            raise ValueError("La oferta ya ha sido finalizada.")

        user = User.objects.get(current_offer_passenger_id=self.id)
        user.current_offer_passenger = None
        user.currently_passenger = False
        user.save()

        self.delete()

    def finish_by_passenger(self, stars_to_driver):
        if not self.accepted:
            raise ValueError("La oferta no ha sido aceptada.")
        if self.finished:
            raise ValueError("La oferta ya ha sido finalizada.")
        if stars_to_driver not in range(1, 6):
            raise ValueError("Las estrellas deben estar entre 1 y 5.")

        passenger = User.objects.get(current_offer_passenger_id=self.id)
        passenger.total_trips_passenger += 1
        passenger.current_offer_passenger = None
        passenger.currently_passenger = False

        self.finished = True
        self.trip.vehicle.owner.total_stars_driver += stars_to_driver

        self.save()

    def finish_by_driver(self, stars_to_user):
        if not self.accepted:
            raise ValueError("La oferta no ha sido aceptada.")
        if self.finished:
            raise ValueError("La oferta ya ha sido finalizada.")
        if stars_to_user not in range(1, 6):
            raise ValueError("Las estrellas deben estar entre 1 y 5.")

        passenger = User.objects.get(current_offer_passenger_id=self.id)
        passenger.total_trips_passenger += 1
        passenger.total_stars_passenger += stars_to_user
        passenger.current_offer_passenger = None
        passenger.currently_passenger = False

        self.finished = True
        self.stars_to_user = stars_to_user

        self.save()

    def rate_passenger(self, stars_to_user):
        if not self.finished:
            raise ValueError("La oferta no ha sido finalizada.")
        if stars_to_user not in range(1, 6):
            raise ValueError("Las estrellas deben estar entre 1 y 5.")

        self.stars_to_user = stars_to_user
        self.save()

    def rate_driver(self, stars_to_driver):
        if not self.finished:
            raise ValueError("La oferta no ha sido finalizada.")
        if stars_to_driver not in range(1, 6):
            raise ValueError("Las estrellas deben estar entre 1 y 5.")

        self.stars_to_driver = stars_to_driver
        self.save()
