from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView as refresh

from .views.register_view import register
from .views.verify_account_view import verify_account
from .views.resend_code_view import resend_code
from .views.login_view import login
from .views.profile_views import get_profile, update_profile

auth_patterns = [
    path("auth/register/", register, name="register"),
    path("auth/verify/", verify_account, name="verify"),
    path("auth/resend_code/", resend_code, name="resend"),
    path("auth/login/", login, name="login"),
    path("auth/login/refresh/", refresh.as_view(), name="refresh"),
]

profile_patterns = [
    path("profile/", get_profile, name="profile"),
    path("profile/update/", update_profile, name="update_profile"),
]

urlpatterns = auth_patterns + profile_patterns
