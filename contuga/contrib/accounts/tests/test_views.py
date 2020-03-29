from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .. import constants as account_constants
from ..models import Account

UserModel = get_user_model()


class AccountsTestCase(TestCase):
    def setUp(self):
        user = UserModel.objects.create_user(
            email="john.doe@example.com", password="password"
        )
        self.account = Account.objects.create(
            name="Account name", currency=account_constants.BGN, owner=user
        )
        self.client.force_login(user)

    def test_list(self):
        url = reverse("accounts:list")
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert queryset is correct
        self.assertQuerysetEqual(
            response.context["account_list"],
            Account.objects.all(),
            transform=lambda x: x,
        )

        # Assert account fields are used
        fields = [
            self.account.name,
            self.account.get_currency_display(),
        ]
        for field in fields:
            self.assertContains(response=response, text=field)

    def test_detail(self):
        url = reverse("accounts:detail", kwargs={"pk": self.account.pk})
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct model is retrieved
        self.assertEqual(response.context["account"], self.account)

        # Assert account fields are used
        fields = [
            self.account.name,
            self.account.get_currency_display(),
            self.account.description,
        ]
        for field in fields:
            self.assertContains(response=response, text=field)

    def test_create_get(self):
        url = reverse("accounts:create")
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        data = {
            "name": "New account name",
            "currency": account_constants.EUR,
            "description": "New account description",
        }
        old_account_count = Account.objects.count()

        url = reverse("accounts:create")
        response = self.client.post(url, data=data, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert new account is created
        new_account_count = Account.objects.count()
        self.assertEqual(new_account_count, old_account_count + 1)

        # Assert account is saved correctly
        account = Account.objects.order_by("created_at").last()
        account_data = {
            "name": account.name,
            "currency": account.currency,
            "description": account.description,
        }
        self.assertDictEqual(account_data, data)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("accounts:detail", kwargs={"pk": account.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_update_get(self):
        url = reverse("accounts:update", kwargs={"pk": self.account.pk})
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert instance is correct
        instance = response.context.get("object")
        self.assertEqual(instance, self.account)

        # Assert initial form data is correct
        form = response.context.get("form")
        form_data = {
            "name": form.initial["name"],
            "description": form.initial["description"],
        }
        expected_data = {
            "name": self.account.name,
            "description": self.account.description,
        }
        self.assertDictEqual(form_data, expected_data)

    def test_update(self):
        data = {"name": "New account name", "description": "New account description"}

        url = reverse("accounts:update", kwargs={"pk": self.account.pk})
        response = self.client.post(url, data=data, follow=True)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("accounts:detail", kwargs={"pk": self.account.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Assert account is updated
        account = Account.objects.get(pk=self.account.pk)
        account_data = {"name": account.name, "description": account.description}
        self.assertDictEqual(account_data, data)

    def test_delete(self):
        old_account_count = Account.objects.count()

        url = reverse("accounts:delete", kwargs={"pk": self.account.pk})
        response = self.client.post(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert account is deleted
        new_account_count = Account.objects.count()
        self.assertEqual(new_account_count, old_account_count - 1)
        with self.assertRaises(Account.DoesNotExist):
            Account.objects.get(pk=self.account.pk)
