from django.urls import path

from .views import vehicle_views

urlpatterns = [
    path('vehicles/', vehicle_views.get_user_vehicles, name = 'get_user_vehicles'),
    path('vehicles/create', vehicle_views.create_vehicle, name = 'create_vehicle'),
]
