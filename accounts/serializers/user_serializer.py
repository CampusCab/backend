from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from ..models.user import User

class UserSerializer(ModelSerializer):

    password = serializers.CharField(write_only = True)

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

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user