from django import forms
from django.contrib import admin

from accounts.models import User
from .models import Vehicle, Trip, Offer


class VehicleAdmin(admin.ModelAdmin):
    list_display = ("id", "license", "owner", "model", "max_passengers")
    search_fields = ("owner__email", "license", "model")
    ordering = ("owner",)


class OfferInline(admin.StackedInline):
    model = Offer
    extra = 0
    fields = (
        "passenger_id",
        "amount",
        "accepted",
        "finished",
        "stars_to_user",
        "stars_to_driver",
    )


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
    inlines = [OfferInline]


class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "passenger_id",
        "trip",
        "amount",
        "accepted",
        "finished",
        "stars_to_user",
        "stars_to_driver",
    )
    search_fields = ("trip__origin", "trip__destination")
    ordering = ("trip",)


admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Trip, TripAdmin)
admin.site.register(Offer, OfferAdmin)
