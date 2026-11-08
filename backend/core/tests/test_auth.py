import re

from django.core import mail
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase


@override_settings(
    DEBUG=False,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="AgriVigil AI <noreply@example.com>",
)
class AuthEmailFlowTests(APITestCase):
    def test_registration_email_verification_and_login(self):
        response = self.client.post(
            "/api/auth/register/",
            {"email": "farmer@example.com", "password": "SecureP@ssword2026!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("debug_otp_code", response.data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["farmer@example.com"])
        otp_code = re.search(r"\b\d{6}\b", mail.outbox[0].body).group()

        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": "farmer@example.com", "otp_code": otp_code},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)

        response = self.client.post(
            "/api/auth/login/",
            {"email": "farmer@example.com", "password": "SecureP@ssword2026!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], "farmer@example.com")

    def test_password_reset_sends_otp_without_returning_it(self):
        from django.contrib.auth import get_user_model

        get_user_model().objects.create_user(
            email="farmer@example.com",
            password="SecureP@ssword2026!",
        )

        response = self.client.post(
            "/api/auth/forgot-password/",
            {"email": "farmer@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("debug_reset_token", response.data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["farmer@example.com"])
        self.assertRegex(mail.outbox[0].body, r"\b\d{6}\b")
