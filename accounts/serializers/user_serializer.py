from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from ..models.user import User

class UserSerializer(ModelSerializer):

    password = serializers.CharField(write_only = True)
    email = serializers.EmailField(error_messages = {"invalid": "Ingresa un correo válido"})
    phone = serializers.CharField(error_messages = {"invalid": "Ingresa un número de teléfono válido"})
    first_name = serializers.CharField(error_messages = {"required": "Ingresa tu nombre"})
    last_name = serializers.CharField(error_messages = {"required": "Ingresa tu apellido"})

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "password",
            "first_name",
            "last_name"
        ]

    def validate_email(self, value):
        if not value.endswith("@unal.edu.co"):
            raise serializers.ValidationError("Usa un correo institucional")

        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user