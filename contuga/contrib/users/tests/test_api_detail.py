from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from ..models import User

UserModel = get_user_model()


class UserDetailTestCase(APITestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.client.force_login(self.user)

    def test_get(self):
        url = reverse("user-detail", args=[self.user.pk])
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "email": self.user.email,
            "last_login": self.user.last_login.astimezone().isoformat(),
            "date_joined": self.user.date_joined.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_get_other_users(self):
        user = UserModel.objects.create_user("richard.roe@example.com", "password")

        url = reverse("user-detail", args=[user.pk])

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_patch(self):
        url = reverse("user-detail", args=[self.user.pk])

        data = {"current_password": "password", "new_password": "new_password"}

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert user is updated
        user = User.objects.get(pk=self.user.pk)
        self.assertNotEqual(user.password, self.user.password)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "email": self.user.email,
            "last_login": self.user.last_login.astimezone().isoformat(),
            "date_joined": self.user.date_joined.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_patch_other_users(self):
        user = UserModel.objects.create_user("richard.roe@example.com", "password")

        url = reverse("user-detail", args=[user.pk])

        data = {"current_password": "password", "new_password": "new_password"}

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert user is not updated
        retrieved_user = User.objects.get(pk=user.pk)
        self.assertEqual(retrieved_user.password, user.password)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_patch_other_fields(self):
        url = reverse("user-detail", args=[self.user.pk])

        data = {
            "current_password": "password",
            "new_password": "new_password",
            "email": "richard.roe@example.com",
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert user email is not updated
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.email, self.user.email)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "email": self.user.email,
            "last_login": self.user.last_login.astimezone().isoformat(),
            "date_joined": self.user.date_joined.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_delete(self):
        old_user_count = User.objects.count()

        url = reverse("user-detail", args=[self.user.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 204)

        # Assert user is deleted
        new_user_count = User.objects.count()
        self.assertEqual(new_user_count, old_user_count - 1)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.user.pk)

    def test_cannot_delete_other_users(self):
        user = UserModel.objects.create_user("richard.roe@example.com", "password")
        old_user_count = User.objects.count()

        url = reverse("user-detail", args=[user.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert user is not deleted
        new_user_count = User.objects.count()
        self.assertEqual(new_user_count, old_user_count)
