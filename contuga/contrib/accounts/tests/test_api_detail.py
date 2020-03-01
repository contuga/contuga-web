from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from ..models import Account
from .. import constants
from . import utils


UserModel = get_user_model()


class AccountDetailTestCase(APITestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.account = Account.objects.create(
            name="Account name",
            currency=constants.BGN,
            owner=self.user,
            description="Account description",
            is_active=True,
        )

        token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def test_get(self):
        url = reverse("account-detail", args=[self.account.pk])
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": self.account.name,
            "currency": self.account.currency,
            "owner": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "description": self.account.description,
            "is_active": self.account.is_active,
            "updated_at": self.account.updated_at.astimezone().isoformat(),
            "created_at": self.account.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_get_accounts_of_other_users(self):
        account = utils.create_user_and_account()

        url = reverse("account-detail", args=[account.pk])
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_patch(self):
        url = reverse("account-detail", args=[self.account.pk])

        data = {
            "name": "New account name",
            "description": "New account description",
            "is_active": False,
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        account = Account.objects.get(pk=self.account.pk)

        # Assert account is updated
        self.assertNotEqual(account.updated_at, self.account.updated_at)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": data["name"],
            "currency": account.currency,
            "owner": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "description": data["description"],
            "is_active": data["is_active"],
            "updated_at": account.updated_at.astimezone().isoformat(),
            "created_at": self.account.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_cannot_patch_accounts_of_other_users(self):
        account = utils.create_user_and_account()

        url = reverse("account-detail", args=[account.pk])

        data = {
            "name": "New account name",
            "description": "New account description",
            "is_active": False,
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert account is not updated
        retrieved_account = Account.objects.get(pk=account.pk)
        self.assertEqual(retrieved_account.updated_at, account.updated_at)

        # Assert correct data is returned
        expected_response = {"detail": _("Not found.")}

        self.assertDictEqual(response.json(), expected_response)

    def test_owner_field_is_ignored_on_patch(self):
        url = reverse("account-detail", args=[self.account.pk])

        user = UserModel.objects.create_user("richard.roe@example.com", "password")

        data = {
            "owner": reverse("user-detail", args=[user.pk]),
            "name": "New account name",
            "description": "New account description",
            "is_active": False,
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        account = Account.objects.get(pk=self.account.pk)

        # Assert account owner is not updated
        self.assertEqual(account.owner, self.account.owner)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": data["name"],
            "currency": self.account.currency,
            "owner": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "description": data["description"],
            "is_active": data["is_active"],
            "updated_at": account.updated_at.astimezone().isoformat(),
            "created_at": self.account.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_currency_field_is_ignored_on_patch(self):
        url = reverse("account-detail", args=[self.account.pk])

        data = {
            "currency": constants.EUR,
            "name": "New account name",
            "description": "New account description",
            "is_active": False,
        }

        response = self.client.patch(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        account = Account.objects.get(pk=self.account.pk)

        # Assert account currency is not updated
        self.assertEqual(account.currency, self.account.currency)

        # Assert correct data is returned
        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(url),
            "name": data["name"],
            "currency": account.currency,
            "owner": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "description": data["description"],
            "is_active": data["is_active"],
            "updated_at": account.updated_at.astimezone().isoformat(),
            "created_at": self.account.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_delete(self):
        old_account_count = Account.objects.count()

        url = reverse("account-detail", args=[self.account.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 204)

        # Assert account is deleted
        new_account_count = Account.objects.count()
        self.assertEqual(new_account_count, old_account_count - 1)

        with self.assertRaises(Account.DoesNotExist):
            Account.objects.get(pk=self.account.pk)

    def test_cannot_delete_accounts_of_other_users(self):
        account = utils.create_user_and_account()
        old_account_count = Account.objects.count()

        url = reverse("account-detail", args=[account.pk])
        response = self.client.delete(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 404)

        # Assert account is not deleted
        new_account_count = Account.objects.count()
        self.assertEqual(new_account_count, old_account_count)