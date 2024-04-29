from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from ..serializers.user_serializer import UserSerializer
from ..utils.email_utils import generate_code, send_email


@api_view(["POST"])
def register(request):

    serializer = UserSerializer(data=request.data)

    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    code = generate_code()
    user.verification_code = code

    if send_email(user, code):
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

    user = serializer.save()
