from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import OneTimeCode


class AuthWithoutEmailTests(APITestCase):
    def test_registration_activates_account_and_logs_in_without_email(self):
        response = self.client.post(
            "/api/auth/register/",
            {"email": "farmer@example.com", "password": "SecureP@ssword2026!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access_token", response.data)
        self.assertEqual(response.data["user"]["email"], "farmer@example.com")
        self.assertTrue(get_user_model().objects.get(email="farmer@example.com").is_active)
        self.assertEqual(OneTimeCode.objects.count(), 0)

        response = self.client.post(
            "/api/auth/login/",
            {"email": "farmer@example.com", "password": "SecureP@ssword2026!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], "farmer@example.com")

    def test_email_verification_and_password_reset_routes_are_disabled(self):
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"email": "farmer@example.com", "otp_code": "123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.post(
            "/api/auth/forgot-password/",
            {"email": "farmer@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
