from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from ..serializers.vehicle_serializer import VehicleSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_vehicles(request):
    user = request.user
    vehicles = list(user.vehicle_set.values())

    return JsonResponse(vehicles, status = status.HTTP_200_OK, safe = False)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_vehicle(request):
    user = request.user
    data = request.data | {"owner": user.id}
    serializer = VehicleSerializer(data = data)

    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return JsonResponse(serializer.data, status = status.HTTP_201_CREATED)