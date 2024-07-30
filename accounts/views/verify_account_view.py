from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from ..models.user import User


@api_view(["POST"])
def verify_account(request):
    email = request.data.get("email")
    verification_code = request.data.get("verification_code")

    fields = {"email": email, "verification_code": verification_code}

    errors = {
        field: "El campo es requerido"
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

    if not user.verify(verification_code):
        return JsonResponse(
            {"error": "El código de verificación es incorrecto"},
            status=status.HTTP_400_BAD_REQUEST
        )

    return JsonResponse(
        {"message": "Cuenta verificada correctamente"},
        status=status.HTTP_200_OK
    )
