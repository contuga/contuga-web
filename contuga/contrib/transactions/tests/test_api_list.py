from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from contuga.contrib.transactions.constants import INCOME
from contuga.contrib.categories.models import Category
from contuga.contrib.accounts.models import Account
from contuga.contrib.accounts import constants as account_constants
from ..models import Transaction
from . import utils

UserModel = get_user_model()


class TransactionListTestCase(APITestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.category = Category.objects.create(
            name="Category name", author=self.user, description="Category description"
        )
        self.account = Account.objects.create(
            name="Account name",
            currency=account_constants.BGN,
            owner=self.user,
            description="Account description",
        )
        self.transaction = Transaction.objects.create(
            amount="100.10",
            author=self.user,
            category=self.category,
            account=self.account,
            description="Transaction description",
        )
        self.client.force_login(self.user)

    def test_get(self):
        url = reverse("transaction-list")

        # Creating another independent transaction with its own user, category
        # and account to make sure the currently logged in user cannot see the
        # transactions of other users
        utils.create_independent_transaction()

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

        category = Category.objects.create(
            name="Second category name",
            author=self.user,
            description="Second category description",
        )
        account = Account.objects.create(
            name="Second account name",
            currency=account_constants.BGN,
            owner=self.user,
            description="Second account description",
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
        transaction = Transaction.objects.order_by("pk").last()

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

        user = UserModel.objects.create_user("richard.roe@example.com", "password")
        category = Category.objects.create(
            name="Second category name",
            author=self.user,
            description="Second category description",
        )
        account = Account.objects.create(
            name="Second account name",
            currency=account_constants.BGN,
            owner=self.user,
            description="Second account description",
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
        transaction = Transaction.objects.order_by("pk").last()

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
