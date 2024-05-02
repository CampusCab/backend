from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializers.login_serializer import LoginSerializer
from ..serializers.user_serializer import UserSerializer

@api_view(["POST"])
def login(request):
    serializer = LoginSerializer(data = request.data)

    if not serializer.is_valid():
        return JsonResponse(data = serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    user = serializer.validated_data

    if not user.is_active:
        return JsonResponse(data = {"error": "User is not active"}, status = status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(user)
    tokens: dict[str, str] = get_tokens_for_user(user)

    data = {
        "user": serializer.data,
        "tokens": tokens
    }

    return JsonResponse(data, status = status.HTTP_200_OK)



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh_token": str(refresh),
        "access_token": str(refresh.access_token),
    }