from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls"), name="accounts"),
    path("", include("core.urls"), name="core"),
]
