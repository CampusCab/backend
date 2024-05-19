from django.db.models import F
from django.utils import timezone
from django.db import models
from .vehicle import Vehicle

ALLOWED_PLACES = ["Campus El Volador", "Campus Del Río", "Campus Robledo"]


class Trip(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    description = models.TextField()
    finished = models.BooleanField(default=False)

    @classmethod
    def get_available_trips(cls):
        now = timezone.now()

        trips = cls.objects.filter(start_time__gte=now, finished=False)
        trips = trips.annotate(offer_count=models.Count("offer"))
        trips = trips.filter(offer_count__lt=F('vehicle__max_passengers'))

        return trips

    def verify_trip_for_campus(self):
        if self.origin not in ALLOWED_PLACES and self.destination not in ALLOWED_PLACES:
            return False
        return True

    def clean(self):
        if self.start_time < timezone.now():
            raise ValueError("La fecha de inicio no puede ser en el pasado.")

        if self.origin == self.destination:
            raise ValueError("El origen y el destino no pueden ser iguales.")

        if not self.verify_trip_for_campus():
            raise ValueError(
                "El origen y/o el destino deben ser campus de la universidad."
            )

        self.save()
        self.vehicle.owner.start_as_driver(self)

    def finish(self):
        if self.finished:
            raise ValueError("El viaje ya ha sido finalizado.")

        for offer in self.offer_set.all():
            if not offer.finished:
                raise ValueError("Aún hay ofertas sin finalizar.")

        self.finished = True
        self.save()

    def __str__(self):
        return f"{self.id} - from {self.origin} at {self.start_time}"
