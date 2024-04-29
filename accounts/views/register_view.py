from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from ..models.user import User
from ..serializers.user_serializer import UserSerializer
from ..utils.email_utils import generate_code, send_email


@api_view(["POST"])
def register(request):
    serializer = UserSerializer(data = request.data)

    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data["email"]

    if User.objects.filter(email = email).exists():
        return JsonResponse({"message": "Este correo ya está registrado"}, status = status.HTTP_400_BAD_REQUEST)

    code = generate_code()
    user = serializer.save()

    user.verification_code = code
    user.save()

    if not send_email(user, code):
        user.delete()
        return JsonResponse({"message": "No se pudo enviar el correo de verificación"}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
