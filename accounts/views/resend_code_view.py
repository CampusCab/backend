from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from ..models.user import User
from ..utils.email_utils import generate_code, send_email


@api_view(["POST"])
def resend_code(request):
    email = request.data.get("email")

    fields = {"email": email}
    errors = {
        field: "Este campo es requerido"
        for field, value in fields.items()
        if value is None
    }

    if errors:
        return JsonResponse(errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "El usuario no existe"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if user.is_active:
        return JsonResponse(
            {"error": "La cuenta ya ha sido activada"},
            status=status.HTTP_400_BAD_REQUEST
        )

    code = generate_code()
    user.verification_code = code

    if send_email(user, code):
        return JsonResponse(
            {"message": "Código de verificación reenviado"},
            status=status.HTTP_200_OK
        )

    user.save()
