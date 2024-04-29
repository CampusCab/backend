from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from ..models.user import User

@api_view(["POST"])
def verify_account(request):

    email = request.data.get("email")
    verification_code = request.data.get("verification_code")

    try:
        user = User.objects.get(email = email)
    except User.DoesNotExist:
        return JsonResponse({"error": "User does not exists"}, status=status.HTTP_400_BAD_REQUEST)

    if not user.verify(verification_code):
        return JsonResponse({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"message": "Account verified successfully"}, status=status.HTTP_200_OK)
