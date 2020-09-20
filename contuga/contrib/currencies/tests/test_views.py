from django.test import TestCase
from django.urls import reverse

from contuga.contrib.currencies.models import Currency
from contuga.mixins import TestMixin


class CurrencyViewTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.currency = self.create_currency()
        self.client.force_login(self.user)

    def test_list(self):
        url = reverse("currencies:list")
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert queryset is correct
        self.assertQuerysetEqual(
            response.context["currency_list"],
            Currency.objects.all(),
            transform=lambda x: x,
        )

        # Assert currency fields are used
        fields = [self.currency.name, self.currency.code, self.currency.nominal]
        for field in fields:
            self.assertContains(response=response, text=field)

    def test_detail(self):
        url = reverse("currencies:detail", kwargs={"pk": self.currency.pk})
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct model is retrieved
        self.assertEqual(response.context["currency"], self.currency)

        # Assert currency fields are used
        fields = [self.currency.name, self.currency.code, self.currency.nominal]
        for field in fields:
            self.assertContains(response=response, text=field)

    def test_create_get(self):
        url = reverse("currencies:create")
        response = self.client.get(url)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        data = {"name": "New currency name", "code": "BGN", "nominal": 1}
        old_currency_count = Currency.objects.count()

        url = reverse("currencies:create")
        response = self.client.post(url, data=data, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert new currency is created
        new_currency_count = Currency.objects.count()
        self.assertEqual(new_currency_count, old_currency_count + 1)

        # Assert currency is saved correctly
        currency = Currency.objects.order_by("created_at").last()
        currency_data = {
            "name": currency.name,
            "code": "BGN",
            "nominal": currency.nominal,
        }
        self.assertDictEqual(currency_data, data)

        # Assert user is redirected to detail view
        self.assertRedirects(
            response,
            reverse("currencies:detail", kwargs={"pk": currency.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_delete(self):
        old_currency_count = Currency.objects.count()

        url = reverse("currencies:delete", kwargs={"pk": self.currency.pk})
        response = self.client.post(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert currency is deleted
        new_currency_count = Currency.objects.count()
        self.assertEqual(new_currency_count, old_currency_count - 1)
        with self.assertRaises(Currency.DoesNotExist):
            Currency.objects.get(pk=self.currency.pk)
