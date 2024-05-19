from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView as refresh_token

from .views import (
    register_view,
    verify_account_view,
    resend_code_view,
    login_view,
    profile_views,
)

auth_patterns = [
    path("auth/register/", register_view.register, name="register"),
    path("auth/verify/", verify_account_view.verify_account, name="verify"),
    path("auth/resend_code/", resend_code_view.resend_code, name="resend"),
    path("auth/login/", login_view.login, name="login"),
    path("auth/login/refresh/", refresh_token.as_view(), name="refresh_token"),
]

profile_patterns = [
    path("profile/", profile_views.get_profile, name="profile"),
    path("profile/update/", profile_views.update_profile, name="update_profile"),
]

urlpatterns = auth_patterns + profile_patterns
