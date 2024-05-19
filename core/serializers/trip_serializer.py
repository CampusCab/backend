from rest_framework import serializers

from ..models import Trip

ALLOWED_PLACES = ["Campus El Volador", "Campus Del Río", "Campus Robledo"]


class TripSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)

    class Meta:
        model = Trip
        fields = ['vehicle', 'origin', 'destination', 'start_time', 'description']

    # Validate that the origin and destination are not the same
    def validate(self, data):
        if data['origin'] == data['destination']:
            raise serializers.ValidationError("El origen y el destino no pueden ser iguales")

        if data['origin'] not in ALLOWED_PLACES and data['destination'] not in ALLOWED_PLACES:
            raise serializers.ValidationError("El origen y el destino no son válidos")

        return data