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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_trip(request):
    user: User = request.user

    if not request.data.get("vehicle"):
        return JsonResponse(
            {"message": "Vehicle ID is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        vehicle = Vehicle.objects.get(id=request.data.get("vehicle"), owner=user)
    except Vehicle.DoesNotExist:
        return JsonResponse(
            {"message": "Vehicle does not exist for this user"},
            status=status.HTTP_400_BAD_REQUEST,
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_trip(request):
    user: User = request.user

    if not user.has_active_trip():
        return JsonResponse(
            {"message": "User does not have an active trip"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = TripSerializer(user.get_active_trip())
    data = serializer.data

    if user.currently_passenger:
        offer = user.current_offer_passenger
        data = data | {"accepted": offer.accepted}
    elif user.currently_driver:
        offers = user.current_trip_driver.offer_set.all()
        data = data | {"offers": CurrentOfferSerializer(offers, many=True).data}

    return JsonResponse(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_available_trips(request):
    user: User = request.user

    if user.has_active_trip():
        return JsonResponse(
            {"message": "User already has an active trip"},
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
            {"message": "Trip does not exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    if user.has_active_trip():
        return JsonResponse(
            {"message": "User already has an active trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if trip.offer_set.filter(passenger_id=user.id).exists():
        return JsonResponse(
            {"message": "User already has an offer for this trip"},
            status=status.HTTP_400_BAD_REQUEST,
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
def accept_offer(request, trip_id, offer_id):
    user: User = request.user

    if not user.has_active_trip():
        return JsonResponse(
            {"message": "User does not have an active trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.currently_driver or user.current_trip_driver is None:
        return JsonResponse(
            {"message": "User is not a driver right now"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user.current_trip_driver.id != trip_id:
        return JsonResponse(
            {"message": "User is not the driver of this trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offer = user.current_trip_driver.offer_set.get(id=offer_id)
    except Offer.DoesNotExist:
        return JsonResponse(
            {"message": "Offer does not exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        offer.accept()
    except ValueError as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = OfferSerializer(offer)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_offer(request, trip_id, offer_id):
    user: User = request.user

    if not user.has_active_trip():
        return JsonResponse(
            {"message": "User does not have an active trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.currently_driver or user.current_trip_driver is None:
        return JsonResponse(
            {"message": "User is not a driver right now"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user.current_trip_driver.id != trip_id:
        return JsonResponse(
            {"message": "User is not the driver of this trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offer = user.current_trip_driver.offer_set.get(id=offer_id)
    except Offer.DoesNotExist:
        return JsonResponse(
            {"message": "Offer does not exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        offer.reject()
    except ValueError as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"message": "Offer rejected"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def finish_trip_as_passenger(request, trip_id):
    user: User = request.user

    if not user.has_active_trip():
        return JsonResponse(
            {"message": "User does not have an active trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.currently_passenger or user.current_offer_passenger is None:
        return JsonResponse(
            {"message": "User is not a passenger right now"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user.current_offer_passenger.trip.id != trip_id:
        return JsonResponse(
            {"message": "User is not a passenger of this trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    stars = request.data.get("stars_to_driver")

    if not stars:
        return JsonResponse(
            {"message": "Stars to driver are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    offer = user.current_offer_passenger

    try:
        offer.finish_by_passenger(stars)
    except ValueError as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"message": "Trip finished"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_user_from_trip(request, trip_id, user_id):
    user: User = request.user

    if not user.has_active_trip():
        return JsonResponse(
            {"message": "User does not have an active trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.currently_driver or user.current_trip_driver is None:
        return JsonResponse(
            {"message": "User is not a driver right now"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    stars = request.data.get("stars_to_user")

    if not stars:
        return JsonResponse(
            {"message": "Stars to user are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_to_remove = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse(
            {"message": "User to remove does not exist"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user_to_remove.current_offer_passenger is None:
        return JsonResponse(
            {"message": "User to remove is not a passenger right now"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user_to_remove.current_offer_passenger.trip.id != trip_id:
        return JsonResponse(
            {"message": "User to remove is not a passenger of this trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    offer = user_to_remove.current_offer_passenger

    if offer.trip != user.current_trip_driver:
        return JsonResponse(
            {"message": "User to remove is not a passenger of this trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offer.finish_by_driver(stars)
    except ValueError as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    trip = user.current_trip_driver

    try:
        trip.finish()
        return JsonResponse({"message": "Trip finished"}, status=status.HTTP_200_OK)
    except ValueError as _:
        return JsonResponse(
            {"message": "User removed from trip"}, status=status.HTTP_200_OK
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
            {"message": "User is not the driver of this trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offer = Offer.objects.get(trip_id=trip_id, passenger_id=user_id)
    except Offer.DoesNotExist:
        return JsonResponse(
            {"message": "Passenger is not a passenger of this trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offer.rate_passenger(stars, user_id)
    except ValueError as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"message": "Passenger rated"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_driver_as_passenger(request, trip_id):
    user: User = request.user

    stars = request.data.get("stars")

    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return JsonResponse(
            {"message": "Trip does not exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        offer = Offer.objects.get(trip_id=trip_id, passenger_id=user.id)
    except Offer.DoesNotExist:
        return JsonResponse(
            {"message": "User is not a passenger of this trip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        offer.rate_driver(stars)
    except ValueError as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"message": "Driver rated"}, status=status.HTTP_200_OK)
