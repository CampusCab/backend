from django.urls import path

from .views import vehicle_views, trip_views

vehicle_patterns = [
    path('vehicles/', vehicle_views.get_user_vehicles, name='get_user_vehicles'),
    path('vehicles/<int:vehicle_id>', vehicle_views.get_vehicle, name='get_vehicle'),
    path('vehicles/create', vehicle_views.create_vehicle, name='create_vehicle'),
    path('vehicles/update/<int:vehicle_id>', vehicle_views.update_vehicle, name='update_vehicle')
]

general_trip_patterns = [
    path('trips/avaliable', trip_views.get_available_trips, name='get_available_trips'),
    path('trips/current', trip_views.get_current_trip, name='get_current_trip'),
    path('trips/past', trip_views.get_driver_trips, name='get_driver_trips'),
    path('trips/create', trip_views.create_trip, name='create_trip')
]

current_trip_patterns = [
    path('trips/<int:trip_id>/offer', trip_views.send_offer, name='send_offer'),
    path('trips/<int:trip_id>/accept', trip_views.accept_offer, name='accept_offer'),
    path('trips/<int:trip_id>/reject', trip_views.reject_offer, name='reject_offer'),
    path('trips/<int:trip_id>/finish', trip_views.finish_trip_as_passenger, name='finish_trip_as_passenger'),
    path('trips/<int:trip_id>/cancel', trip_views.cancel_trip_as_passenger, name='cancel_trip_as_passenger'),
    path('trips/<int:trip_id>/remove/<int:user_id>', trip_views.remove_user_from_trip, name='remove_user_from_trip')
]

trip_patterns = general_trip_patterns + current_trip_patterns
urlpatterns = trip_patterns + vehicle_patterns
