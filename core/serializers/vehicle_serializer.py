from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from ..models.vehicle import Vehicle
from accounts.models.user import User


class VehicleSerializer(ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset = User.objects.all(), write_only = True)
    license = serializers.CharField(error_messages = {"required": "Ingresa la placa"})
    model = serializers.CharField(error_messages = {"required": "Ingresa el modelo"})
    max_passengers = serializers.IntegerField(error_messages = {"required": "Ingresa el número máximo de pasajeros"})

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "owner",
            "license",
            "model",
            "max_passengers"
        ]

    def create(self, validated_data):
        vehicle = Vehicle.objects.create(**validated_data)
        return vehicle