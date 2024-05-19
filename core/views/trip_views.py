from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from ..models import Trip, Vehicle
from ..serializers.trip_serializer import TripSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_trip(request):
    user: User = request.user

    if not request.data.get("vehicle"):
        return JsonResponse(
            {"message": "Vehicle is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        vehicle = Vehicle.objects.get(id=request.data.get("vehicle"), owner=user)
    except Vehicle.DoesNotExist:
        return JsonResponse(
            {"message": "Vehicle does not exist for this user"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if user.has_active_trip():
        active_trip = user.get_active_trip()

        return JsonResponse(
            {"message": f"User already has an active trip (ID: {active_trip.id})"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = TripSerializer(data=request.data)

    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    trip = serializer.save()
    user.start_as_driver(trip)

    serializer.save(user=user, vehicle=vehicle)
    return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)


# Conseguir el viaje actual del usuario
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_trip(request):
    user: User = request.user

    if not user.has_active_trip():
        return JsonResponse(
            {"message": "User does not have an active trip"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = TripSerializer(user.get_active_trip())
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


# Conseguir todos los viajes disponibles para el usuario
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_available_trips(request):
    return JsonResponse({"message": "Get available trips"}, status=status.HTTP_200_OK)


# Enviar oferta para un viaje
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_offer(request):
    return JsonResponse({"message": "Send offer"}, status=status.HTTP_200_OK)


# Aceptar oferta como conductor
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_offer(request):
    return JsonResponse({"message": "Accept offer"}, status=status.HTTP_200_OK)


# Rechazar oferta como conductor
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_offer(request):
    return JsonResponse({"message": "Reject offer"}, status=status.HTTP_200_OK)


# Terminar viaje siendo pasajero y calificar al conductor
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def finish_trip_as_passenger(request):
    return JsonResponse(
        {"message": "Finish trip as passenger"}, status=status.HTTP_200_OK
    )


# Cancelar viaje siendo pasajero
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_trip_as_passenger(request):
    return JsonResponse(
        {"message": "Cancel trip as passenger"}, status=status.HTTP_200_OK
    )


# Eliminar un usuario de un viaje y calificar al usuario. Si ya no hay pasajeros, terminar el viaje
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_user_from_trip(request):
    return JsonResponse({"message": "Remove user from trip"}, status=status.HTTP_200_OK)


# Conseguir todos los viajes en los que el usuario ha sido conductor, total recogido y deuda con la plataforma
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_driver_trips(request):
    return JsonResponse({"message": "Get driver trips"}, status=status.HTTP_200_OK)
