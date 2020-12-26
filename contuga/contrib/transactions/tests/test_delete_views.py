from django.test import TestCase
from django.urls import reverse

from contuga.contrib.transactions.models import Transaction
from contuga.mixins import TestMixin


class TransactionViewTests(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.category = self.create_category()
        self.currency = self.create_currency()
        self.account = self.create_account()
        self.transaction = self.create_transaction()
        self.client.force_login(self.user)

    def test_delete(self):
        old_transaction_count = Transaction.objects.count()

        url = reverse("transactions:delete", kwargs={"pk": self.transaction.pk})
        response = self.client.post(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert transaction is deleted
        new_transaction_count = Transaction.objects.count()
        self.assertEqual(new_transaction_count, old_transaction_count - 1)
        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(pk=self.transaction.pk)
