import json
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from contuga.contrib.transactions.models import Transaction
from contuga.contrib.transactions.constants import EXPENDITURE, INCOME
from contuga.contrib.transactions.forms import InternalTransferForm
from contuga.contrib.accounts.models import Account
from contuga.contrib.accounts.constants import BGN, EUR

UserModel = get_user_model()


class InternalTransferViewTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.account = self.create_account()
        self.client.force_login(self.user)

    def create_account(self, prefix="First", currency=BGN, user=None):
        if not user:
            user = self.user
        return Account.objects.create(
            name=f"{prefix} account name",
            currency=currency,
            owner=user,
            description=f"{prefix} account description",
        )

    def test_transfer_get(self):
        second_account = self.create_account(prefix="Second")
        third_account = self.create_account(prefix="Third", currency=EUR)

        url = reverse("transactions:internal_transfer_form")
        response = self.client.get(url)

        expected_account_list = json.dumps(
            {
                self.account.pk: self.account.currency,
                second_account.pk: second_account.currency,
                third_account.pk: third_account.currency,
            }
        )

        self.assertEqual(response.context["accounts"], expected_account_list)
        self.assertIsInstance(response.context["form"], InternalTransferForm)

    def test_tansfer_to_account_of_same_currency(self):
        second_account = self.create_account(prefix="Second")

        data = {
            "from_account": self.account.pk,
            "to_account": second_account.pk,
            "amount": "145.33",
            "description": "Transfer description",
        }
        old_transaction_count = Transaction.objects.count()

        url = reverse("transactions:internal_transfer_form")
        response = self.client.post(url, data=data, follow=True)

        # Assert user is redirected to success view
        self.assertRedirects(
            response,
            reverse("transactions:internal_transfer_success"),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Assert new transaction is created
        new_transaction_count = Transaction.objects.count()
        self.assertEqual(new_transaction_count, old_transaction_count + 2)

        # Assert transactions are saved correctly
        expenditure = Transaction.objects.order_by("created_at").first()
        expenditure_data = {
            "type": expenditure.type,
            "amount": expenditure.amount,
            "author": expenditure.author,
            "category": expenditure.category,
            "account": expenditure.account,
            "description": expenditure.description,
        }
        expected_expenditure_data = {
            "type": EXPENDITURE,
            "amount": Decimal("145.33"),
            "author": self.user,
            "category": None,
            "account": self.account,
            "description": data["description"],
        }
        self.assertDictEqual(expenditure_data, expected_expenditure_data)

        income = Transaction.objects.order_by("created_at").last()
        income_data = {
            "type": income.type,
            "amount": income.amount,
            "author": income.author,
            "category": income.category,
            "account": income.account,
            "description": income.description,
        }
        expected_income_data = {
            "type": INCOME,
            "amount": Decimal("145.33"),
            "author": self.user,
            "category": None,
            "account": second_account,
            "description": data["description"],
        }
        self.assertDictEqual(income_data, expected_income_data)

        # Assert the new transactions are removed from the session
        session = self.client.session
        self.assertIsNone(session.get("expenditure"))
        self.assertIsNone(session.get("income"))

        # Assert the new transactions are added to the context
        expected_context_expenditure = {
            "amount": str(expenditure.amount),
            "currency": expenditure.currency,
            "url": expenditure.get_absolute_url(),
            "account": {
                "name": expenditure.account.name,
                "url": expenditure.account.get_absolute_url(),
            },
        }

        expected_context_income = {
            "amount": str(income.amount),
            "currency": income.currency,
            "url": income.get_absolute_url(),
            "account": {
                "name": income.account.name,
                "url": income.account.get_absolute_url(),
            },
        }

        self.assertDictEqual(
            response.context["expenditure"], expected_context_expenditure
        )

        self.assertDictEqual(response.context["income"], expected_context_income)

    def test_tansfer_to_account_of_different_currency(self):
        second_account = self.create_account(prefix="Second", currency=EUR)

        data = {
            "from_account": self.account.pk,
            "to_account": second_account.pk,
            "amount": "101.00",
            "rate": "0.51",
        }
        old_transaction_count = Transaction.objects.count()

        url = reverse("transactions:internal_transfer_form")
        response = self.client.post(url, data=data, follow=True)

        # Assert user is redirected to success view
        self.assertRedirects(
            response,
            reverse("transactions:internal_transfer_success"),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

        # Assert new transaction is created
        new_transaction_count = Transaction.objects.count()
        self.assertEqual(new_transaction_count, old_transaction_count + 2)

        # Assert transactions are saved correctly
        expenditure = Transaction.objects.order_by("created_at").first()
        expenditure_data = {
            "type": expenditure.type,
            "amount": expenditure.amount,
            "author": expenditure.author,
            "category": expenditure.category,
            "account": expenditure.account,
            "description": expenditure.description,
        }
        expected_expenditure_data = {
            "type": EXPENDITURE,
            "amount": Decimal("101.00"),
            "author": self.user,
            "category": None,
            "account": self.account,
            "description": "",
        }
        self.assertDictEqual(expenditure_data, expected_expenditure_data)

        income = Transaction.objects.order_by("created_at").last()
        income_data = {
            "type": income.type,
            "amount": income.amount,
            "author": income.author,
            "category": income.category,
            "account": income.account,
            "description": income.description,
        }
        expected_income_data = {
            "type": INCOME,
            "amount": Decimal("51.51"),
            "author": self.user,
            "category": None,
            "account": second_account,
            "description": "",
        }
        self.assertDictEqual(income_data, expected_income_data)

        # Assert the new transactions are removed from the session
        session = self.client.session
        self.assertIsNone(session.get("expenditure"))
        self.assertIsNone(session.get("income"))

    def test_session_data(self):
        second_account = self.create_account(prefix="Second")

        data = {
            "from_account": self.account.pk,
            "to_account": second_account.pk,
            "amount": "200.00",
        }

        url = reverse("transactions:internal_transfer_form")
        self.client.post(url, data=data, follow=False)

        expenditure = Transaction.objects.order_by("created_at").first()
        income = Transaction.objects.order_by("created_at").last()

        # Assert the new transactions are added to the session before redirect
        expected_session_expenditure = {
            "amount": str(expenditure.amount),
            "currency": expenditure.currency,
            "url": expenditure.get_absolute_url(),
            "account": {
                "name": expenditure.account.name,
                "url": expenditure.account.get_absolute_url(),
            },
        }

        expected_session_income = {
            "amount": str(income.amount),
            "currency": income.currency,
            "url": income.get_absolute_url(),
            "account": {
                "name": income.account.name,
                "url": income.account.get_absolute_url(),
            },
        }

        session = self.client.session
        self.assertEqual(session["expenditure"], expected_session_expenditure)
        self.assertEqual(session["income"], expected_session_income)

    def test_success_view_redirects_to_form_if_session_data_is_missing(self):
        url = reverse("transactions:internal_transfer_success")
        response = self.client.get(url)

        self.assertRedirects(
            response,
            reverse("transactions:internal_transfer_form"),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
