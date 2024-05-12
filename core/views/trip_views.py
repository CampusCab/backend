from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


# Ofrecer el viaje
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_trip(request):
    return JsonResponse({"message": "Create trip"}, status=status.HTTP_200_OK)

# Conseguir el viaje actual del usuario
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_trip(request):
    return JsonResponse({"message": "Get current trip"}, status=status.HTTP_200_OK)

# Conseguir todos los viajes disponibles para el usuario
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_available_trips(request):
    return JsonResponse({"message": "Get available trips"}, status=status.HTTP_200_OK)

# Aceptar oferta
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_offer(request):
    return JsonResponse({"message": "Accept offer"}, status=status.HTTP_200_OK)

# Rechazar oferta
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_offer(request):
    return JsonResponse({"message": "Reject offer"}, status=status.HTTP_200_OK)

# Terminar viaje siendo pasajero y calificar al conductor
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def finish_trip_as_passenger(request):
    return JsonResponse({"message": "Finish trip as passenger"}, status=status.HTTP_200_OK)

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
