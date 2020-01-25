from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from contuga.contrib.transactions.forms import InternalTransferForm
from contuga.contrib.accounts.models import Account
from contuga.contrib.accounts.constants import BGN, EUR

UserModel = get_user_model()


class InternalTransferFormTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user("john.doe@example.com", "password")
        self.account = self.create_acount()

    def create_acount(self, prefix="First", currency=BGN, user=None):
        if not user:
            user = self.user
        return Account.objects.create(
            name=f"{prefix} account name",
            currency=currency,
            owner=user,
            description=f"{prefix} account description",
        )

    def test_tansfer(self):
        second_account = self.create_acount(prefix="Second")

        data = {
            "from_account": self.account.pk,
            "to_account": second_account.pk,
            "amount": "101.00",
        }

        form = InternalTransferForm(user=self.user, data=data)

        self.assertTrue(form.is_valid())

        expected_cleaned_data = {
            "from_account": self.account,
            "to_account": second_account,
            "amount": Decimal("101.00"),
            "rate": None,
        }

        self.assertDictEqual(form.cleaned_data, expected_cleaned_data)

    def test_tansfer_to_account_of_different_currency(self):
        second_account = self.create_acount(prefix="Second", currency=EUR)

        data = {
            "from_account": self.account.pk,
            "to_account": second_account.pk,
            "amount": "101.00",
            "rate": "1.98",
        }

        form = InternalTransferForm(user=self.user, data=data)

        self.assertTrue(form.is_valid())

        expected_cleaned_data = {
            "from_account": self.account,
            "to_account": second_account,
            "amount": Decimal("101.00"),
            "rate": Decimal("1.98"),
        }

        self.assertDictEqual(form.cleaned_data, expected_cleaned_data)

    def test_tansfer_with_negative_amount(self):
        second_account = self.create_acount(prefix="Second")

        data = {
            "from_account": self.account.pk,
            "to_account": second_account.pk,
            "amount": "-10",
        }

        form = InternalTransferForm(user=self.user, data=data)

        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors,
            {"amount": [_("Ensure this value is greater than or equal to 0.")]},
        )

    def test_tansfer_to_account_of_different_currency_with_rate_missing(self):
        second_account = self.create_acount(prefix="Second", currency=EUR)

        data = {
            "from_account": self.account.pk,
            "to_account": second_account.pk,
            "amount": "101.00",
        }

        form = InternalTransferForm(user=self.user, data=data)

        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors,
            {
                "__all__": [
                    _(
                        "You need to specify exchange rate if the "
                        "two accounts are of different currencies."
                    )
                ]
            },
        )

    def test_tansfer_to_the_same_account(self):
        data = {
            "from_account": self.account.pk,
            "to_account": self.account.pk,
            "amount": "101.00",
        }

        form = InternalTransferForm(user=self.user, data=data)

        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors, {"__all__": [_("The two accounts shouldn't be the same.")]}
        )

    def test_tansfer_from_wrong_account(self):
        user = UserModel.objects.create_user("john.roe@example.com", "password")
        wrong_account = self.create_acount(prefix="Wrong", user=user)

        data = {
            "from_account": wrong_account.pk,
            "to_account": self.account.pk,
            "amount": "101.00",
        }

        form = InternalTransferForm(user=self.user, data=data)

        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors,
            {
                "from_account": [
                    _(
                        "Select a valid choice. That choice is not one "
                        "of the available choices."
                    )
                ]
            },
        )

    def test_tansfer_to_wrong_account(self):
        user = UserModel.objects.create_user("john.roe@example.com", "password")
        wrong_account = self.create_acount(prefix="Wrong", user=user)

        data = {
            "from_account": self.account.pk,
            "to_account": wrong_account.pk,
            "amount": "101.00",
        }

        form = InternalTransferForm(user=self.user, data=data)

        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors,
            {
                "to_account": [
                    _(
                        "Select a valid choice. That choice is not one "
                        "of the available choices."
                    )
                ]
            },
        )
