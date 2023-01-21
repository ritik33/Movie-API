from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import jwt
from .models import User
from .renderers import UserRenderer
from .utils import Util
from .serializers import (
    UserRegistrationSerializer,
    UserEmailVerificationSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    UserProfileSerializer,
    UserPasswordChangeSerializer,
    RequestPasswordResetEmailSerializer,
    UserPasswordResetSerializer,
)


class UserRegistrationView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = user.tokens()
        current_site = get_current_site(request).domain
        verify = reverse("email-verify")
        verificationLink = (
            "http://" + current_site + verify + "?token=" + token["access"]
        )
        email_body = (
            "Hi "
            + user.username
            + "\n"
            + "Click on the link below to verify your email \n"
            + verificationLink
            + "\nLink will expire in 10 minutes."
        )
        data = {
            "email_subject": "Verify your email",
            "email_body": email_body,
            "to_email": user.email,
        }
        print("Email verification link:", verificationLink)
        try:
            Util.send_email(data)
        except:
            return Response(
                {"msg": "Error while sending verification email."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"msg": "Verification email sent.", "token": token},
            status=status.HTTP_201_CREATED,
        )


class UserEmailVerificationView(generics.GenericAPIView):
    serializer_class = UserEmailVerificationSerializer

    token_param = openapi.Parameter(
        "token",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[token_param])
    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.save(update_fields=["is_verified"])
                return Response(
                    {"email": "Verified successfully."}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"email": "Already Verified."}, status=status.HTTP_200_OK
                )
        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Token expired."}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLogoutView(generics.GenericAPIView):
    serializer_class = UserLogoutSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileView(generics.GenericAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPasswordChangeView(generics.GenericAPIView):
    serializer_class = UserPasswordChangeSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"msg": "Password changed successfully"}, status=status.HTTP_200_OK
        )


class RequestPasswordResetEmailView(generics.GenericAPIView):
    serializer_class = RequestPasswordResetEmailSerializer
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get("email")
        user = User.objects.get(email=email)
        # encode user.id(int) to base64
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        current_site = get_current_site(request).domain
        reset = reverse("password-reset", kwargs={"uidb64": uidb64, "token": token})
        passwordResetLink = "http://" + current_site + reset
        email_body = (
            "Hi "
            + user.username
            + "\n"
            + "Click on the link below to reset your password\n"
            + passwordResetLink
            + "\nLink will expire in 10 minutes."
        )
        data = {
            "email_subject": "Reset your password",
            "email_body": email_body,
            "to_email": user.email,
        }
        print("Password reset link:", passwordResetLink)
        try:
            Util.send_email(data)
        except:
            return Response(
                {"msg": "Error while sending password reset email."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"msg": "Password reset email sent."},
            status=status.HTTP_200_OK,
        )


class UserPasswordResetView(generics.GenericAPIView):
    serializer_class = UserPasswordResetSerializer
    renderer_classes = [UserRenderer]

    def post(self, request, uidb64, token):
        serializer = self.serializer_class(
            data=request.data, context={"uidb64": uidb64, "token": token}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"msg": "Password reset successfully."}, status=status.HTTP_200_OK
        )
