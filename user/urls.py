from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserEmailVerificationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    UserPasswordChangeView,
    RequestPasswordResetEmailView,
    UserPasswordResetView,
)


urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("email-verify/", UserEmailVerificationView.as_view(), name="email-verify"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("password-change/", UserPasswordChangeView.as_view(), name="password-change"),
    path(
        "request-password-reset-email/",
        RequestPasswordResetEmailView.as_view(),
        name="request-password-reset-email",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        UserPasswordResetView.as_view(),
        name="password-reset",
    ),
]
