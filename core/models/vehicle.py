from django.db import models
from accounts.models import User

class Vehicle(models.Model):
    owner = models.ForeignKey(User,on_delete = models.CASCADE)
    license = models.CharField(max_length = 6)
    model = models.CharField(max_length = 255)
    max_passengers = models.IntegerField()

    def clean(self):
        if self.max_passengers < 1: raise ValueError("El vehículo debe tener al menos un pasajero.")

    def __str__(self):
        return f"{self.license} - {self.model}"