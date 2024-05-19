from django.contrib import admin
from .models import Vehicle, Trip, Offer


class VehicleAdmin(admin.ModelAdmin):
    list_display = ("id", "license", "owner", "model", "max_passengers")
    search_fields = ("owner__email", "license", "model")
    ordering = ("owner",)


class TripAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vehicle",
        "origin",
        "destination",
        "start_time",
        "description",
        "finished",
    )
    search_fields = ("vehicle__license", "origin", "destination", "description")
    ordering = ("start_time",)


class OfferAdmin(admin.ModelAdmin):
    list_display = ("id", "trip", "amount", "accepted", "finished", "stars_to_user")
    search_fields = ("trip__origin", "trip__destination")
    ordering = ("trip",)


admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Trip, TripAdmin)
admin.site.register(Offer, OfferAdmin)
