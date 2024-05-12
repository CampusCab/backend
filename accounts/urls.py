from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView as refresh

from .views.register_view import register
from .views.verify_account_view import verify_account
from .views.resend_code_view import resend_code
from .views.login_view import login

urlpatterns = [
    path("register/", register, name = "register"),
    path("verify/", verify_account, name = "verify"),
    path("resend_code/", resend_code, name = "resend"),
    path("login/", login, name = "login"),
    path("login/refresh/", refresh.as_view(), name = "refresh"),
]
