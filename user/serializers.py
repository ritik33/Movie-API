from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


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
