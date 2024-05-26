from rest_framework import serializers

from .offer_serializer import (
    PastOfferPassengerSerializer,
    PastOffersDriverSerializer,
)
from ..models import Trip

ALLOWED_PLACES = ["Campus El Volador", "Campus Del Río", "Campus Robledo"]


class TripSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    description = serializers.CharField(required=False)

    class Meta:
        model = Trip
        fields = ["id", "vehicle", "origin", "destination", "start_time", "description"]

    # Validate that the origin and destination are not the same
    def validate(self, data):
        if data["origin"] == data["destination"]:
            raise serializers.ValidationError(
                "El origen y el destino no pueden ser iguales"
            )

        if (
            data["origin"] not in ALLOWED_PLACES
            and data["destination"] not in ALLOWED_PLACES
        ):
            raise serializers.ValidationError("El origen y el destino no son válidos")

        return data


class PastTripPassengerSerializer(serializers.ModelSerializer):
    offer = PastOfferPassengerSerializer(read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "vehicle",
            "origin",
            "destination",
            "start_time",
            "description",
            "offer",
        ]


class PastTripDriverSerializer(serializers.ModelSerializer):
    offers = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            "id",
            "vehicle",
            "origin",
            "destination",
            "start_time",
            "description",
            "offers",
        ]

    def get_offers(self, obj):
        offers = obj.offer_set.all()
        return PastOffersDriverSerializer(offers, many=True).data
