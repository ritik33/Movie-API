from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .models import User
from .renderers import UserRenderer
from .serializers import (
    UserRegistrationSerializer,
    UserEmailVerificationSerializer,
    UserLoginSerializer,
)
from django.urls import reverse
from .utils import Util
import jwt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserRegistrationView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
