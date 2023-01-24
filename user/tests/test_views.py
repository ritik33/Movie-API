from django.urls import reverse
from django.core import mail
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from ..models import User


class UserRegistrationTests(APITestCase):
    fake = Faker()
    email = fake.email()
    username = email.split("@")[0]
    password = fake.password()
    registration_url = reverse("register")
    email_verify_url = reverse("email-verify")

    def test_registration_with_email_verification(self):
        data = {
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "password2": self.password,
        }
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # check one verification email
        self.assertEqual(len(mail.outbox), 1)
        verification_link = mail.outbox[0].body.splitlines()[2]
        token = verification_link.split("/")[-1][7:]
        data = {"token": token}
        response = self.client.get(self.email_verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_registration_with_weak_password(self):
        password = self.fake.password(
            upper_case=False, lower_case=False, special_chars=False
        )
        data = {
            "email": self.email,
            "username": self.username,
            "password": password,
            "password2": password,
        }
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginLogoutTests(APITestCase):
    fake = Faker()
    email = fake.email()
    username = email.split("@")[0]
    password = fake.password()
    data = {
        "email": email,
        "password": password,
    }
    login_url = reverse("login")
    logout_url = reverse("logout")

    def setUp(self):
        user = User.objects.create_user(
            email=self.email, username=self.username, password=self.password
        )
        user.is_verified = True
        user.save(update_fields=["is_verified"])

    def login(self):
        response = self.client.post(self.login_url, self.data)
        return response

    def test_login(self):
        response = self.login()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        login_response = self.login()
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        tokens = login_response.data["tokens"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer %s" % tokens["access"])
        data = {"refresh": tokens["refresh"]}
        response = self.client.post(self.logout_url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_with_invalid_token(self):
        login_response = self.login()
        token = login_response.data["tokens"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer %s" % token)
        data = {"refresh": "qwer.asdf.zxcv"}
        response = self.client.post(self.logout_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserPasswordTests(APITestCase):
    fake = Faker()
    email = fake.email()
    username = email.split("@")[0]
    password = fake.password()
    login_url = reverse("login")
    data = {
        "email": email,
        "password": password,
    }
    password_reset_email_url = reverse("request-password-reset-email")
    password_change_url = reverse("password-change")

    def setUp(self):
        user = User.objects.create_user(
            email=self.email, username=self.username, password=self.password
        )
        user.is_verified = True
        user.save(update_fields=["is_verified"])

    def test_password_change(self):
        login_response = self.client.post(self.login_url, self.data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        token = login_response.data["tokens"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer %s" % token)
        password = self.fake.password()
        data = {"password": password, "password2": password}
        response = self.client.post(self.password_change_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset(self):
        data = {"email": self.email}
        reset_email_response = self.client.post(self.password_reset_email_url, data)
        self.assertEqual(reset_email_response.status_code, status.HTTP_200_OK)
        # check one password reset email
        self.assertEqual(len(mail.outbox), 1)
        reset_link = mail.outbox[0].body.splitlines()[2]
        uidb64, token = reset_link.split("/")[-3:-1]
        password_reset_url = reverse(
            "password-reset", kwargs={"uidb64": uidb64, "token": token}
        )
        password = self.fake.password()
        data = {"password": password, "password2": password}
        response = self.client.post(password_reset_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
