from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.mixins import TestMixin

from ..constants import EXPENDITURE, INCOME
from ..models import Transaction


class TransactionListTestCase(APITestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user()
        self.category = self.create_category()
        self.currency = self.create_currency()
        self.account = self.create_account()
        self.transaction = self.create_transaction(amount="100.10")

        token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def create_independent_transaction(self):
        user = self.create_user(email="richard.roe@example.com")
        category = self.create_category(author=user)
        account = self.create_account(owner=user)
        return self.create_expenditure(
            amount="100.10", author=user, category=category, account=account
        )

    def test_get(self):
        url = reverse("transaction-list")

        # Creating another independent transaction with its own user, category
        # and account to make sure the currently logged in user cannot see the
        # transactions of other users
        self.create_independent_transaction()

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": response.wsgi_request.build_absolute_uri(
                        reverse("transaction-detail", args=[self.transaction.pk])
                    ),
                    "type": self.transaction.type,
                    "amount": self.transaction.amount,
                    "author": response.wsgi_request.build_absolute_uri(
                        reverse("user-detail", args=[self.user.pk])
                    ),
                    "category": response.wsgi_request.build_absolute_uri(
                        reverse("category-detail", args=[self.category.pk])
                    ),
                    "account": response.wsgi_request.build_absolute_uri(
                        reverse("account-detail", args=[self.account.pk])
                    ),
                    "description": self.transaction.description,
                    "updated_at": self.transaction.updated_at.astimezone().isoformat(),
                    "created_at": self.transaction.created_at.astimezone().isoformat(),
                }
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_post(self):
        url = reverse("transaction-list")

        category = self.create_category(
            name="Second category name", description="Second category description"
        )
        account = self.create_account(
            name="Second account name", description="Second account description"
        )

        data = {
            "type": INCOME,
            "amount": "300.30",
            "category": reverse("category-detail", args=[category.pk]),
            "account": reverse("account-detail", args=[account.pk]),
            "description": "New transaction description",
        }

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        transaction = Transaction.objects.order_by("created_at").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("transaction-detail", args=[transaction.pk])
            ),
            "type": data["type"],
            "amount": data["amount"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "category": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[category.pk])
            ),
            "account": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[account.pk])
            ),
            "description": data["description"],
            "updated_at": transaction.updated_at.astimezone().isoformat(),
            "created_at": transaction.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_author_field_is_ignored_on_post(self):
        url = reverse("transaction-list")

        user = self.create_user(email="richard.roe@example.com", password="password")
        category = self.create_category(
            name="Second category name",
            author=self.user,
            description="Second category description",
        )
        account = self.create_account(
            name="Second account name", description="Second account description"
        )

        data = {
            "type": INCOME,
            "amount": "300.30",
            "author": reverse("user-detail", args=[user.pk]),
            "category": reverse("category-detail", args=[category.pk]),
            "account": reverse("account-detail", args=[account.pk]),
            "description": "New transaction description",
        }

        response = self.client.post(url, data=data, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 201)

        # Assert correct data is returned
        transaction = Transaction.objects.order_by("created_at").last()

        expected_response = {
            "url": response.wsgi_request.build_absolute_uri(
                reverse("transaction-detail", args=[transaction.pk])
            ),
            "type": data["type"],
            "amount": data["amount"],
            "author": response.wsgi_request.build_absolute_uri(
                reverse("user-detail", args=[self.user.pk])
            ),
            "category": response.wsgi_request.build_absolute_uri(
                reverse("category-detail", args=[category.pk])
            ),
            "account": response.wsgi_request.build_absolute_uri(
                reverse("account-detail", args=[account.pk])
            ),
            "description": data["description"],
            "updated_at": transaction.updated_at.astimezone().isoformat(),
            "created_at": transaction.created_at.astimezone().isoformat(),
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_create_income_with_wrong_category(self):
        category = self.create_category(transaction_type=EXPENDITURE)

        data = {
            "type": INCOME,
            "amount": "200",
            "author": reverse("user-detail", args=[self.user.pk]),
            "category": reverse("category-detail", args=[category.pk]),
            "account": reverse("account-detail", args=[self.account.pk]),
            "description": "Transaction description",
        }
        old_transaction_count = Transaction.objects.count()

        url = reverse("transaction-list")
        response = self.client.post(url, data=data, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 400)

        # Assert correct data is returned
        expected_message = _("Invalid hyperlink - Object does not exist.")
        self.assertEqual(response.json(), {"category": [expected_message]})

        # Assert new transaction is not created
        new_transaction_count = Transaction.objects.count()
        self.assertEqual(new_transaction_count, old_transaction_count)

    def test_create_expenditure_with_wrong_category(self):
        category = self.create_category(transaction_type=INCOME)

        data = {
            "type": EXPENDITURE,
            "amount": "200",
            "author": reverse("user-detail", args=[self.user.pk]),
            "category": reverse("category-detail", args=[category.pk]),
            "account": reverse("account-detail", args=[self.account.pk]),
            "description": "Transaction description",
        }
        old_transaction_count = Transaction.objects.count()

        url = reverse("transaction-list")
        response = self.client.post(url, data=data, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 400)

        # Assert correct data is returned
        expected_message = _("Invalid hyperlink - Object does not exist.")
        self.assertEqual(response.json(), {"category": [expected_message]})

        # Assert new transaction is not created
        new_transaction_count = Transaction.objects.count()
        self.assertEqual(new_transaction_count, old_transaction_count)
