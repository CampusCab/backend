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

    list_display = ("id", "email", "phone", "first_name", "last_name", "is_staff", "is_active", "verification_code")
    list_filter = ("is_staff",)

    fieldsets = (
        ("Information", {"fields": ("email", "phone", "password", "first_name", "last_name")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "user_permissions")}),
    )

    search_fields = ("email", "phone", "first_name", "last_name")
    ordering = ("id",)

admin.site.register(User, CustomUserAdmin)