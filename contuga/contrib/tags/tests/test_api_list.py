from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.mixins import TestMixin

from ..models import Tag


class TagListTestCase(APITestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.tag = self.create_tag()

        token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def create_user_and_tag(self, email="richard.roe@example.com"):
        user = self.create_user(email, "password")

        return self.create_tag(name="Other tag name", author=user)

    def test_get(self):
        self.currency = self.create_currency()
        self.account = self.create_account()
        self.transaction = self.create_transaction(tags=[self.tag])

        url = reverse("tag-list")

        # Creating another user and tag to make sure the currently
        # logged in user cannot see the tags of other users
        self.create_user_and_tag()

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
                        reverse("tag-detail", args=[self.tag.pk])
                    ),
                    "name": self.tag.name,
                    "transactions": [
                        response.wsgi_request.build_absolute_uri(
                            reverse("transaction-detail", args=[self.transaction.pk])
                        )
                    ],
                    "author": response.wsgi_request.build_absolute_uri(
                        reverse("user-detail", args=[self.user.pk])
                    ),
                    "updated_at": self.tag.updated_at.astimezone().isoformat(),
                    "created_at": self.tag.created_at.astimezone().isoformat(),
                }
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_post(self):
        url = reverse("tag-list")

        data = {"name": "New tag name"}

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        tag = Tag.objects.order_by("created_at").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("tag-detail", args=[tag.pk])
            ),
            "name": tag.name,
            "transactions": [],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "updated_at": tag.updated_at.astimezone().isoformat(),
            "created_at": tag.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_author_field_is_ignored_on_post(self):
        url = reverse("tag-list")
        user = self.create_user(email="richard.roe@example.com", password="password")

        data = {
            "name": "New tag name",
            "author": reverse("user-detail", args=[user.pk]),
        }

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        tag = Tag.objects.order_by("created_at").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("tag-detail", args=[tag.pk])
            ),
            "name": tag.name,
            "transactions": [],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "updated_at": tag.updated_at.astimezone().isoformat(),
            "created_at": tag.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)
