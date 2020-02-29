from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

UserModel = get_user_model()


class ContugaTestCase(APITestCase):
    def test_token_is_required(self):
        url = reverse("user-list")

        UserModel.objects.create_user("john.doe@example.com", "password")

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 403)

        # Assert correct data is returned
        expected_response = {
            "detail": _("Authentication credentials were not provided.")
        }

        self.assertDictEqual(response.json(), expected_response)
