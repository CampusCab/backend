from django.db import models
from .trip import Trip

class Offer(models.Model):
    trip = models.ForeignKey(Trip, on_delete = models.CASCADE)
    amount = models.IntegerField()
    accepted = models.BooleanField(default = False)
    finished = models.BooleanField(default = False)
    stars = models.IntegerField()

    def accept(self):
        if self.accepted: raise ValueError("La oferta ya ha sido aceptada.")
        if self.finished: raise ValueError("La oferta ya ha sido finalizada.")

        self.accepted = True
        self.save()

    def finish(self, stars):
        if not self.accepted: raise ValueError("La oferta no ha sido aceptada.")
        if self.finished: raise ValueError("La oferta ya ha sido finalizada.")
        if stars not in range(1, 6): raise ValueError("Las estrellas deben estar entre 1 y 5.")

        self.finished = True
        self.stars = stars
        self.save()