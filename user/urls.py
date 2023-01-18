from django.urls import path
from .views import (
    UserRegistrationView,
    UserEmailVerificationView,
    UserLoginView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("email-verify/", UserEmailVerificationView.as_view(), name="email-verify"),
    path("login/", UserLoginView.as_view(), name="login"),
]
