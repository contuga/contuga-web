from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.mixins import TestMixin

from .. import constants
from ..models import Category


class CategoryListTestCase(APITestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()

        token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def test_get(self):
        url = reverse("category-list")

        # Creating another user and category to make sure the currently
        # logged in user cannot see the categories of other users
        user = self.create_user(email="richard.roe@example.com", password="password")
        self.create_category(author=user)

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        categories = Category.objects.filter(author=self.user)

        expected_response = {
            "count": len(categories),
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": response.wsgi_request.build_absolute_uri(
                        reverse("category-detail", args=[category.pk])
                    ),
                    "name": category.name,
                    "author": response.wsgi_request.build_absolute_uri(
                        reverse("user-detail", args=[self.user.pk])
                    ),
                    "transaction_type": category.transaction_type,
                    "description": category.description,
                    "updated_at": category.updated_at.astimezone().isoformat(),
                    "created_at": category.created_at.astimezone().isoformat(),
                }
                for category in categories
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_post(self):
        url = reverse("category-list")

        data = {
            "name": "New category name",
            "transaction_type": constants.EXPENDITURE,
            "description": "New category description",
        }

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        category = Category.objects.order_by("pk").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[category.pk])
            ),
            "name": data["name"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "transaction_type": data["transaction_type"],
            "description": data["description"],
            "updated_at": category.updated_at.astimezone().isoformat(),
            "created_at": category.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_author_field_is_ignored_on_post(self):
        url = reverse("category-list")

        user = self.create_user(email="richard.roe@example.com", password="password")

        data = {
            "name": "New category name",
            "author": reverse("user-detail", args=[user.pk]),
            "description": "New category description",
        }

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        category = Category.objects.order_by("pk").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[category.pk])
            ),
            "name": data["name"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "transaction_type": category.transaction_type,
            "description": data["description"],
            "updated_at": category.updated_at.astimezone().isoformat(),
            "created_at": category.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)
