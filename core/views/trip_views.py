from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from ..models import Vehicle, Trip, Offer
from ..serializers.offer_serializer import OfferSerializer, CurrentOfferSerializer
from ..serializers.trip_serializer import (
    TripSerializer,
    PastTripPassengerSerializer,
    PastTripDriverSerializer,
)
from ..serializers.vehicle_serializer import VehicleSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_trip(request):
    user: User = request.user

    if not request.data.get("vehicle"):
        return JsonResponse(
            {"message": "El ID del vehiculo es requerido"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        vehicle = Vehicle.objects.get(id=request.data.get("vehicle"), owner=user)
    except Vehicle.DoesNotExist:
        return JsonResponse(
            {"message": "El vehiculo no existe o no pertenece al usuario"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user.has_active_trip():
        active_trip = user.get_active_trip()

        return JsonResponse(
            {"message": f"El usuario ya tiene un viaje activo: {active_trip.id}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = TripSerializer(data=request.data)

    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    trip = serializer.save()
    user.start_as_driver(trip)

    serializer.save(user=user, vehicle=vehicle)
    return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_trip(request):
    user: User = request.user

    if not user.has_active_trip():
        return JsonResponse(
            {"message": "El usuario no tiene un viaje activo"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = TripSerializer(user.get_active_trip())
    data = serializer.data

    if user.currently_passenger:
        offer = user.current_offer_passenger
        data = data | {"accepted": offer.accepted}
    elif user.currently_driver:
        offers = user.current_trip_driver.offer_set.all()
        data = data | {"offers": CurrentOfferSerializer(offers, many=True).data} | {"capacity": user.current_trip_driver.vehicle.max_passengers } | {"vehicle_info": VehicleSerializer(user.current_trip_driver.vehicle).data }

    return JsonResponse(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_available_trips(request):
    user: User = request.user

    if user.has_active_trip():
        return JsonResponse(
            {"message": "El usuario ya tiene un viaje activo"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    trips = Trip.get_available_trips()
    serializer = TripSerializer(trips, many=True)

    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_past_trips(request):
    user: User = request.user

    trips_as_driver = Trip.objects.filter(finished=True, vehicle__owner__id=user.id)
    trips_as_passenger = Trip.objects.filter(finished=True, offer__passenger_id=user.id)

    # append offer to each trip
    for trip in trips_as_passenger:
        offer = trip.offer_set.get(passenger_id=user.id)
        trip.offer = offer

    total_collected = sum(
        offer.amount
        for trip in trips_as_driver
        for offer in trip.offer_set.all()
        if offer.accepted
    )
    total_spent = sum(
        offer.amount
        for trip in trips_as_passenger
        for offer in trip.offer_set.all()
        if offer.accepted
    )

    serializer_driver = PastTripDriverSerializer(trips_as_driver, many=True)
    serializer_passenger = PastTripPassengerSerializer(trips_as_passenger, many=True)

    data = {
        "trips_as_driver": serializer_driver.data,
        "trips_as_passenger": serializer_passenger.data,
        "total_collected": total_collected,
        "total_spent": total_spent,
    }

    return JsonResponse(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_offer(request, trip_id):
    user: User = request.user

    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return JsonResponse(
            {"message": "El viaje no existe"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if user.has_active_trip():
        return JsonResponse(
            {"message": "El usuario ya tiene un viaje activo"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if trip.offer_set.filter(passenger_id=user.id).exists():
        return JsonResponse(
            {"message": "El usuario ya envió una oferta para este viaje"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if trip.finished:
        return JsonResponse(
            data={"message": "El viaje ya finalizó"},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = request.data | {"trip": trip.id, "passenger_id": user.id}
    serializer = OfferSerializer(data=data)

    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    offer = serializer.save()
    user.start_as_passenger(offer)

    serializer.save(user=user, trip=trip)
    return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_offer(request, offer_id):
    user: User = request.user

    if not user.has_active_trip():
        return JsonResponse(
            {"message": "El usuario no tiene un viaje activo"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.currently_driver or user.current_trip_driver is None:
        return JsonResponse(
            {"message": "El usuario no es conductor en este momento"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offer = user.current_trip_driver.offer_set.get(id=offer_id)
    except Offer.DoesNotExist:
        return JsonResponse(
            {"message": "La oferta no existe"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        offer.accept()
    except ValueError as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = OfferSerializer(offer)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_offer(request, offer_id):
    user: User = request.user

    if not user.has_active_trip():
        return JsonResponse(
            {"message": "El usuario no tiene un viaje activo"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.currently_driver or user.current_trip_driver is None:
        return JsonResponse(
            {"message": "El usuario no es conductor en este momento"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offer = user.current_trip_driver.offer_set.get(id=offer_id)
    except Offer.DoesNotExist:
        return JsonResponse(
            {"message": "La oferta no existe"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        offer.reject()
    except ValueError as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse(
        {"message": "Oferta rechazada"},
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def finish_trip_as_passenger(request, trip_id):
    user: User = request.user

    if not user.has_active_trip():
        return JsonResponse(
            {"message": "El usuario no tiene un viaje activo"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.currently_passenger or user.current_offer_passenger is None:
        return JsonResponse(
            {"message": "El usuario no es pasajero en este momento"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user.current_offer_passenger.trip.id != trip_id:
        return JsonResponse(
            {"message": "El usuario no es pasajero de este viaje"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    stars = request.data.get("stars_to_driver")

    if not stars:
        return JsonResponse(
            {"message": "Las estrellas al conductor son requeridas"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    offer = user.current_offer_passenger
    trip = user.current_offer_passenger.trip

    try:
        offer.finish_by_passenger(stars)
    except ValueError as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        trip.finish()
        return JsonResponse(
            {"message": "Viaje finalizado"},
            status=status.HTTP_200_OK
        )
    except ValueError as _:
        return JsonResponse(
            {"message": "Viaje finalizado"},
            status=status.HTTP_200_OK
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_user_from_trip(request, user_id):
    user: User = request.user

    if not user.has_active_trip():
        return JsonResponse(
            {"message": "El usuario no tiene un viaje activo"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.currently_driver or user.current_trip_driver is None:
        return JsonResponse(
            {"message": "El usuario no es conductor en este momento"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_to_remove = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse(
            {"message": "El usuario a remover no existe"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    offer = user_to_remove.current_offer_passenger

    if offer.trip != user.current_trip_driver:
        return JsonResponse(
            {"message": "El usuario a remover no es pasajero de este viaje"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offer.finish_by_driver()
    except ValueError as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    trip = user.current_trip_driver

    try:
        trip.finish()
        return JsonResponse(
            {"message": "Viaje finalizado"},
            status=status.HTTP_200_OK
        )
    except ValueError as _:
        return JsonResponse(
            {"message": "Usuario removido del viaje"},
            status=status.HTTP_200_OK
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_passenger_as_driver(request, trip_id, user_id):
    user: User = request.user

    stars = request.data.get("stars")

    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return JsonResponse(
            {"message": "Trip does not exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    if trip.vehicle.owner.id != user.id:
        return JsonResponse(
            {"message": "El usuario no es el conductor de este viaje"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offer = Offer.objects.get(trip_id=trip_id, passenger_id=user_id)
    except Offer.DoesNotExist:
        return JsonResponse(
            {"message": "El usuario no es pasajero de este viaje"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offer.rate_passenger(stars, user_id)
    except ValueError as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse(
        {"message": "Pasajero calificado"},
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_driver_as_passenger(request, trip_id):
    user: User = request.user

    stars = request.data.get("stars")

    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return JsonResponse(
            {"message": "El viaje no existe"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        offers = list(trip.offer_set.all())

        offer = None
        for o in offers:
            if o.passenger_id == user.id:
                offer = o
                break

    except Offer.DoesNotExist:
        return JsonResponse(
            {"message": "El usuario no es pasajero de este viaje"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if offer is None:
        return JsonResponse(
            {"message": "El usuario no es pasajero de este viaje"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offer.rate_driver(stars)
    except ValueError as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse(
        {"message": "Conductor calificado"},
        status=status.HTTP_200_OK
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def finish_trip_as_driver(request, trip_id):
    user: User = request.user

    if not user.has_active_trip():
        return JsonResponse(
            {"message": "El usuario no tiene un viaje activo"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.currently_driver or user.current_trip_driver is None:
        return JsonResponse(
            {"message": "El usuario no es conductor en este momento"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user.current_trip_driver.id != trip_id:
        return JsonResponse(
            {"message": "El usuario no es conductor de este viaje"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # data came like this: [{"user_id": 1, "stars": 5}, {"user_id": 2, "stars": 4}]
    req_data = request.data

    if not req_data:
        return JsonResponse(
            {"message": "Las estrellas a los usuarios son requeridas"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    trip = user.current_trip_driver

    try:
        trip.finish(req_data)

        return JsonResponse(
            {"message": "Viaje finalizado"},
            status=status.HTTP_200_OK
        )
    except ValueError as _:
        return JsonResponse(
            {"message": "Viaje finalizado"},
            status=status.HTTP_200_OK
        )