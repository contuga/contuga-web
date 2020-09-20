from django.test import TestCase
from django.urls import reverse

from contuga.contrib.currencies.models import Currency
from contuga.mixins import TestMixin


class CurrencyViewTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.client.force_login(self.user)

    def test_update_get(self):
        currency = self.create_currency()
        url = reverse("currencies:update", kwargs={"pk": currency.pk})
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert instance is correct
        instance = response.context.get("object")
        self.assertEqual(instance, currency)

        # Assert initial form data is correct
        form = response.context.get("form")
        form_data = {
            "name": form.initial["name"],
            "code": form.initial["code"],
            "nominal": form.initial["nominal"],
        }
        expected_data = {
            "name": currency.name,
            "code": currency.code,
            "nominal": currency.nominal,
        }
        self.assertDictEqual(form_data, expected_data)

    def test_update(self):
        currency = self.create_currency()
        data = {"name": "New currency name", "code": "EUR", "nominal": 1}

        url = reverse("currencies:update", kwargs={"pk": currency.pk})
        response = self.client.post(url, data=data, follow=True)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("currencies:detail", kwargs={"pk": currency.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Assert currency is updated
        updated_currency = Currency.objects.get(pk=currency.pk)
        currency_data = {
            "name": updated_currency.name,
            "code": updated_currency.code,
            "nominal": updated_currency.nominal,
        }
        self.assertDictEqual(currency_data, data)
