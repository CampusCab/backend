from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated

from accounts.serializers import UserSerializer
from core.models import Trip
from core.serializers.trip_serializer import PastTripDriverSerializer, PastTripPassengerSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    user_serializer = UserSerializer(user)

    vehicles = list(user.vehicle_set.values())
    for vehicle in vehicles:
        vehicle.pop("owner_id")

    data = user_serializer.data
    data["vehicles"] = vehicles

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

    data["trips"] = {
        "as_driver": serializer_driver.data,
        "as_passenger": serializer_passenger.data,
        "total_collected": total_collected,
        "total_spent": total_spent,
    }

    return JsonResponse(data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    user_serializer = UserSerializer(user, data=request.data, partial=True)

    if user_serializer.is_valid():
        user_serializer.save()
        return JsonResponse(user_serializer.data, status=status.HTTP_201_CREATED)

    return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
