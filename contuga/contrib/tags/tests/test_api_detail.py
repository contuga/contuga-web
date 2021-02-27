from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.mixins import TestMixin

from ..models import Tag


class TagDetailTestCase(APITestCase, TestMixin):
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

        url = reverse("tag-detail", args=[self.tag.pk])
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
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

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_get_tags_of_other_users(self):
        tag = self.create_user_and_tag()

        url = reverse("tag-detail", args=[tag.pk])
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_patch(self):
        self.currency = self.create_currency()
        self.account = self.create_account()
        self.transaction = self.create_transaction(tags=[self.tag])

        url = reverse("tag-detail", args=[self.tag.pk])

        data = {"name": "New tag name"}

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        tag = Tag.objects.get(pk=self.tag.pk)

        # Assert tag is updated
        self.assertNotEqual(tag.updated_at, self.tag.updated_at)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": data["name"],
            "transactions": [
                response.wsgi_request.build_absolute_uri(
                    reverse("transaction-detail", args=[self.transaction.pk])
                )
            ],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "updated_at": tag.updated_at.astimezone().isoformat(),
            "created_at": self.tag.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_patch_tags_of_other_users(self):
        tag = self.create_user_and_tag()

        url = reverse("tag-detail", args=[tag.pk])

        data = {"name": "New tag name"}

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert tag is not updated
        retrieved_tag = Tag.objects.get(pk=tag.pk)
        self.assertEqual(retrieved_tag.updated_at, tag.updated_at)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_author_field_is_ignored_on_patch(self):
        self.currency = self.create_currency()
        self.account = self.create_account()
        self.transaction = self.create_transaction(tags=[self.tag])

        url = reverse("tag-detail", args=[self.tag.pk])

        user = self.create_user(email="richard.roe@example.com", password="password")

        data = {
            "author": reverse("user-detail", args=[user.pk]),
            "name": "New tag name",
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        tag = Tag.objects.get(pk=self.tag.pk)

        # Assert tag author is not updated
        self.assertEqual(tag.author, self.tag.author)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": data["name"],
            "transactions": [
                response.wsgi_request.build_absolute_uri(
                    reverse("transaction-detail", args=[self.transaction.pk])
                )
            ],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "updated_at": tag.updated_at.astimezone().isoformat(),
            "created_at": self.tag.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_delete(self):
        old_tag_count = Tag.objects.count()

        url = reverse("tag-detail", args=[self.tag.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 204)

        # Assert tag is deleted
        new_tag_count = Tag.objects.count()
        self.assertEqual(new_tag_count, old_tag_count - 1)

        with self.assertRaises(Tag.DoesNotExist):
            Tag.objects.get(pk=self.tag.pk)

    def test_cannot_delete_tags_of_other_users(self):
        tag = self.create_user_and_tag()
        old_tag_count = Tag.objects.count()

        url = reverse("tag-detail", args=[tag.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert tag is not deleted
        new_tag_count = Tag.objects.count()
        self.assertEqual(new_tag_count, old_tag_count)
