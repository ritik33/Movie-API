from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import serializers
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    # password2 is used to confirm password
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        username = attrs.get("username")
        email = attrs.get("email")

        if not username.isalnum():
            raise serializers.ValidationError("Username should be alpha numeric.")

        user = User(email=email, username=username, password=password)
        try:
            validate_password(password, user)
        except ValidationError as e:
            errors = dict()
            errors["password"] = list(e.messages)
            raise serializers.ValidationError(errors)
        if password != password2:
            raise serializers.ValidationError(
                "Password and Confirm Password doesn't match."
            )
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserEmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=500)

    class Meta:
        model = User
        fields = ["token"]


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    username = serializers.CharField(max_length=50, read_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "username", "tokens"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials, try again.")
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified.")
        return {"email": email, "username": user.username, "tokens": user.tokens()}


class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {"bad_token": ("Token is expired or invalid.")}

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail("bad_token")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username"]


class UserPasswordChangeSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ["password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:
            raise serializers.ValidationError(
                "Password and Confirm Password doesn't match"
            )
        # user is passed in context dict while calling serializer
        user = self.context.get("user")
        try:
            validate_password(password, user)
        except ValidationError as e:
            errors = dict()
            errors["password"] = list(e.messages)
            raise serializers.ValidationError(errors)
        user.set_password(password)
        user.save(update_fields=["password"])
        return attrs


class RequestPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            return attrs
        raise serializers.ValidationError("You are not a registered user")


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        fields = ["password", "password2"]

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:
            raise serializers.ValidationError(
                "Password and confirm password doesn't match."
            )
        uidb64 = self.context.get("uidb64")
        token = self.context.get("token")
        # decode uidb64 to uid
        uid = smart_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Token is not valid or expired.")
        try:
            validate_password(password, user)
        except ValidationError as e:
            errors = dict()
            errors["password"] = list(e.messages)
            raise serializers.ValidationError(errors)
        user.set_password(password)
        user.save(update_fields=["password"])
        return attrs
