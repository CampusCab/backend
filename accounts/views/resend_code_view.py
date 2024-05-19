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
        field: "This field is required"
        for field, value in fields.items()
        if value is None
    }

    if errors:
        return JsonResponse(errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User does not exists"}, status=status.HTTP_400_BAD_REQUEST
        )

    if user.is_active:
        return JsonResponse(
            {"error": "Account is already verified"}, status=status.HTTP_400_BAD_REQUEST
        )

    code = generate_code()
    user.verification_code = code

    if send_email(user, code):
        return JsonResponse(
            {"message": "Code resent successfully"}, status=status.HTTP_200_OK
        )

    user.save()
