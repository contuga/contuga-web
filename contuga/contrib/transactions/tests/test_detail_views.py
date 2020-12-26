from django.test import TestCase
from django.urls import reverse

from contuga.mixins import TestMixin


class TransactionViewTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.category = self.create_category()
        self.currency = self.create_currency()
        self.account = self.create_account()
        self.transaction = self.create_transaction()
        self.client.force_login(self.user)

    def test_detail(self):
        url = reverse("transactions:detail", kwargs={"pk": self.transaction.pk})
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct model is retrieved
        self.assertEqual(response.context["transaction"], self.transaction)

        # Assert transaction fields are used
        fields = [
            self.transaction.amount,
            self.transaction.category.name,
            self.transaction.description,
        ]
        for field in fields:
            self.assertContains(response=response, text=field)
