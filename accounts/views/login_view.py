from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializers.login_serializer import LoginSerializer
from ..serializers.user_serializer import UserSerializer

@api_view(["POST"])
def login(request):
    serializer = LoginSerializer(data = request.data)

    if serializer.is_valid(raise_exception=True):
        user = serializer.validated_data
        serializer = UserSerializer(user)
        tokens: dict[str, str] = get_tokens_for_user(user)
        data = serializer.data
        data["tokens"] = tokens

        return JsonResponse(data = data, status = status.HTTP_200_OK)



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh_token": str(refresh),
        "access_token": str(refresh.access_token),
    }