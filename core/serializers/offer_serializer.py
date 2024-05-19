from rest_framework import serializers
from ..models import Offer


class OfferSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "trip",
            "amount",
            "accepted",
            "finished",
            "finished_by",
            "stars_to_user",
            "stars_to_driver",
        ]
