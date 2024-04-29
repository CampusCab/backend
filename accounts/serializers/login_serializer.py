from rest_framework.serializers import Serializer
from django.contrib.auth import authenticate
from rest_framework import serializers

from ..models.user import User

class LoginSerializer(Serializer):

    email = serializers.CharField()
    password = serializers.CharField(write_only = True)

    def validate(self, data):
        user_auth = authenticate(**data)
        user_active = User.objects.filter(email = data["email"], is_active = True).exists()

        if not user_active: raise serializers.ValidationError("Por favor verifica tu cuenta")
        if not user_auth: raise serializers.ValidationError("Credenciales incorrectas")

        return user_auth