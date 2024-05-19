from rest_framework import serializers
from ..models import Offer


class OfferSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = ["id", "trip", "amount", "accepted", "finished", "stars"]
