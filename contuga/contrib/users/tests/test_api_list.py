from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.mixins import TestMixin

from ..models import User


class UserListTestCase(APITestCase, TestMixin):
    def test_get(self):
        url = reverse("user-list")

        user = self.create_user()

        # Creating another user to make sure the currently logged in user cannot see others
        self.create_user(email="richard.roe@example.com", password="password")

        token, created = Token.objects.get_or_create(user=user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

        self.client.force_login(user)  # Needed for last_login check

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": response.wsgi_request.build_absolute_uri(
                        reverse("user-detail", args=[user.pk])
                    ),
                    "email": user.email,
                    "last_login": user.last_login.astimezone().isoformat(),
                    "date_joined": user.date_joined.astimezone().isoformat(),
                }
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_post(self):
        url = reverse("user-list")

        data = {"email": "john.doe@example.com", "password": "password"}

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        user = User.objects.order_by("pk").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[user.pk])
            ),
            "email": user.email,
            "last_login": None,
            "date_joined": user.date_joined.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)
