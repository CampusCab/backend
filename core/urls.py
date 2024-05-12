from django.urls import path

from .views import vehicle_views, trip_views

urlpatterns = [
    path('vehicles/', vehicle_views.get_user_vehicles, name = 'get_user_vehicles'),
    path('vehicles/create', vehicle_views.create_vehicle, name = 'create_vehicle'),
    path('trips/avaliables', trip_views.get_available_trips, name = 'get_available_trips'),
    path('trips/current', trip_views.get_current_trip, name = 'get_current_trip'),
    path('trips/past', trip_views.get_driver_trips, name = 'get_driver_trips'),
    path('trips/create', trip_views.create_trip, name = 'create_trip'),
    path('trips/<int:trip_id>/accept', trip_views.accept_offer, name = 'accept_offer'),
    path('trips/<int:trip_id>/reject', trip_views.reject_offer, name = 'reject_offer'),
    path('trips/<int:trip_id>/finish', trip_views.finish_trip_as_passenger, name = 'finish_trip_as_passenger'),
    path('trips/<int:trip_id>/remove/<int:passenger_id>', trip_views.remove_user_from_trip, name = 'remove_user_from_trip'),
]
