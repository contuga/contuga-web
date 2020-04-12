from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from contuga.contrib.transactions.models import Transaction
from contuga.contrib.transactions.constants import EXPENDITURE
from contuga.contrib.categories.models import Category
from contuga.contrib.accounts.models import Account
from contuga.contrib.accounts.constants import BGN

UserModel = get_user_model()


class TransactionViewTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.category = Category.objects.create(
            name="Category name",
            author=self.user,
            transaction_type=EXPENDITURE,
            description="Category description",
        )
        self.account = Account.objects.create(
            name="Account name",
            currency=BGN,
            owner=self.user,
            description="Account description",
        )
        self.transaction = Transaction.objects.create(
            amount=100,
            author=self.user,
            category=self.category,
            account=self.account,
            description="Transaction description",
        )
        self.client.force_login(self.user)

    def test_list(self):
        url = reverse("transactions:list")
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert queryset is correct
        self.assertQuerysetEqual(
            response.context["transaction_list"],
            Transaction.objects.all(),
            transform=lambda x: x,
        )

        # Assert transaction fields are used
        fields = [
            self.transaction.type_icon_class,
            self.transaction.amount,
            self.transaction.category.name,
            self.transaction.description,
        ]
        for field in fields:
            self.assertContains(response=response, text=field)

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
