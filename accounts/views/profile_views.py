from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated

from accounts.serializers import UserSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    user_serializer = UserSerializer(user)

    vehicles = list(user.vehicle_set.values())
    for vehicle in vehicles: vehicle.pop("owner_id")

    data = user_serializer.data
    data["vehicles"] = vehicles

    return JsonResponse(data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    user_serializer = UserSerializer(user, data=request.data, partial=True)

    if user_serializer.is_valid():
        user_serializer.save()
        return JsonResponse(user_serializer.data, status=status.HTTP_201_CREATED)

    return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
