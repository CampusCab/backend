from rest_framework import serializers
from ..models import Offer


class OfferSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "trip",
            "passenger_id",
            "amount",
            "accepted",
            "finished",
            "finished_by",
            "stars_to_user",
            "stars_to_driver",
        ]


class PastOfferPassengerSerializer(serializers.ModelSerializer):
    pending_to_rate_driver = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ["id", "amount", "pending_to_rate_driver"]

    def get_pending_to_rate_driver(self, obj):
        return obj.stars_to_driver is None


class PastOffersDriverSerializer(serializers.ModelSerializer):
    pending_to_rate_user = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ["id", "passenger_id", "amount", "pending_to_rate_user"]

    def get_pending_to_rate_user(self, obj):
        return obj.stars_to_user is None


class CurrentOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ["id", "passenger_id", "amount", "accepted", "finished"]
