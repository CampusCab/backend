from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from ..models.user import User


class UserSerializer(ModelSerializer):
    # Required fields
    email = serializers.EmailField(
        error_messages={"invalid": "Ingresa un correo válido"}
    )
    phone = serializers.CharField(
        error_messages={"invalid": "Ingresa un número de teléfono válido"}
    )
    first_name = serializers.CharField(error_messages={"required": "Ingresa tu nombre"})
    last_name = serializers.CharField(
        error_messages={"required": "Ingresa tu apellido"}
    )
    gender = serializers.CharField(required=False)

    # Write only fields
    password = serializers.CharField(write_only=True)

    # Read only fields
    current_trip_driver = PrimaryKeyRelatedField(read_only=True)
    current_offer_passenger = PrimaryKeyRelatedField(read_only=True)
    total_stars_driver = serializers.IntegerField(read_only=True)
    total_trips_driver = serializers.IntegerField(read_only=True)
    rating_driver = serializers.FloatField(read_only=True)
    currently_driver = serializers.BooleanField(read_only=True)
    total_stars_passenger = serializers.IntegerField(read_only=True)
    total_trips_passenger = serializers.IntegerField(read_only=True)
    rating_passenger = serializers.FloatField(read_only=True)
    currently_passenger = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "password",
            "first_name",
            "last_name",
            "gender",
            "total_stars_driver",
            "total_trips_driver",
            "rating_driver",
            "currently_driver",
            "current_trip_driver",
            "total_stars_passenger",
            "total_trips_passenger",
            "rating_passenger",
            "currently_passenger",
            "current_offer_passenger",
        ]

    def validate_email(self, value):
        if not value.endswith("@unal.edu.co"):
            raise serializers.ValidationError("Usa un correo institucional")

        return value

    def validate_gender(self, value):
        if value not in ["M", "F"]:
            raise serializers.ValidationError("Ingresa M o F")

        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
