from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email",)


class CustomUserAdmin(admin.ModelAdmin):
    model = User
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ("id", "email", "phone", "first_name", "last_name", "is_staff", "is_active", "currently_driver", "currently_passenger")
    list_filter = ("is_staff", "currently_driver", "currently_passenger")

    fieldsets = (
        ("Information", {"fields": ("email", "phone", "password", "first_name", "last_name", "gender", "verification_code")}),
        ("Driver", {"fields": ("total_stars_driver", "total_trips_driver", "rating_driver", "currently_driver", "current_trip_driver")}),
        ("Passenger", {"fields": ("total_stars_passenger", "total_trips_passenger", "rating_passenger", "currently_passenger", "current_offer_passenger")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "user_permissions")}),
    )

    search_fields = ("email", "phone", "first_name", "last_name")
    ordering = ("id",)


admin.site.register(User, CustomUserAdmin)