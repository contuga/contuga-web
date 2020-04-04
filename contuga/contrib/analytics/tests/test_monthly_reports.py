from unittest import mock
from decimal import Decimal
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from contuga.contrib.accounts import constants as account_constants
from contuga.contrib.accounts.models import Account
from .. import utils
from . import utils as test_utils


UserModel = get_user_model()


class MonthlyReportsTestCase(TestCase):
    def setUp(self):
        self.now = timezone.now().astimezone()
        self.user = UserModel.objects.create_user(
            email="john.doe@example.com", password="password"
        )
        self.account = Account.objects.create(
            name="Account name", currency=account_constants.BGN, owner=self.user
        )

    def test_report_with_single_account(self):
        income = test_utils.create_income(
            account=self.account, amount=Decimal("310")
        ).amount

        expenditure = test_utils.create_expenditure(
            account=self.account, amount=Decimal("100")
        ).amount

        result = utils.generate_reports(user=self.account.owner)

        reports = test_utils.create_empty_reports(last_date=self.now)
        reports.append(
            {
                "month": self.now.month,
                "year": self.now.year,
                "income": income,
                "expenditures": expenditure,
                "balance": income - expenditure,
            }
        )

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": self.account.currency,
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_report_with_multiple_accounts(self):
        first_account_income = test_utils.create_income(
            account=self.account, amount=Decimal("310.40")
        ).amount

        first_account_expenditure = test_utils.create_expenditure(
            account=self.account, amount=Decimal("100.50")
        ).amount

        second_account = Account.objects.create(
            name="Second account name", currency=account_constants.BGN, owner=self.user
        )

        second_account_income = test_utils.create_income(
            account=second_account, amount=Decimal("1034.44")
        ).amount

        second_account_expenditure = test_utils.create_expenditure(
            account=second_account, amount=Decimal("833.25")
        ).amount

        result = utils.generate_reports(user=self.account.owner)

        first_account_reports = test_utils.create_empty_reports(last_date=self.now)
        second_account_reports = first_account_reports.copy()

        first_account_reports.append(
            {
                "month": self.now.month,
                "year": self.now.year,
                "income": first_account_income,
                "expenditures": first_account_expenditure,
                "balance": first_account_income - first_account_expenditure,
            }
        )

        second_account_reports.append(
            {
                "month": self.now.month,
                "year": self.now.year,
                "income": second_account_income,
                "expenditures": second_account_expenditure,
                "balance": second_account_income - second_account_expenditure,
            }
        )

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": self.account.currency,
                "reports": first_account_reports,
            },
            {
                "pk": second_account.pk,
                "name": second_account.name,
                "currency": second_account.currency,
                "reports": second_account_reports,
            },
        ]

        self.assertListEqual(result, expected_result)

    def test_report_with_no_income(self):
        expenditure = test_utils.create_expenditure(
            account=self.account, amount=Decimal("100.50")
        ).amount

        result = utils.generate_reports(user=self.account.owner)

        reports = test_utils.create_empty_reports(last_date=self.now)
        reports.append(
            {
                "month": self.now.month,
                "year": self.now.year,
                "income": 0,
                "expenditures": expenditure,
                "balance": -expenditure,
            }
        )

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": self.account.currency,
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_report_with_no_expenditures(self):
        income = test_utils.create_income(
            account=self.account, amount=Decimal("310.40")
        ).amount

        result = utils.generate_reports(user=self.account.owner)

        reports = test_utils.create_empty_reports(last_date=self.now)
        reports.append(
            {
                "month": self.now.month,
                "year": self.now.year,
                "income": income,
                "expenditures": 0,
                "balance": income,
            }
        )

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": self.account.currency,
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_report_with_multiple_income_and_expenditures(self):
        first_income = test_utils.create_income(
            account=self.account, amount=Decimal("310.40")
        ).amount

        second_income = test_utils.create_income(
            account=self.account, amount=Decimal("310.40")
        ).amount

        first_expenditure = test_utils.create_expenditure(
            account=self.account, amount=Decimal("100.50")
        ).amount

        second_expenditure = test_utils.create_expenditure(
            account=self.account, amount=Decimal("100.50")
        ).amount

        result = utils.generate_reports(user=self.account.owner)

        reports = test_utils.create_empty_reports(last_date=self.now)
        reports.append(
            {
                "month": self.now.month,
                "year": self.now.year,
                "income": first_income + second_income,
                "expenditures": first_expenditure + second_expenditure,
                "balance": first_income
                + second_income
                - first_expenditure
                - second_expenditure,
            }
        )

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": self.account.currency,
                "reports": reports,
            }
        ]
        self.assertListEqual(result, expected_result)

    def test_accounts_with_no_transactions_are_not_listed(self):
        Account.objects.create(
            name="Second account name", currency=account_constants.BGN, owner=self.user
        )

        income = test_utils.create_income(
            account=self.account, amount=Decimal("310")
        ).amount

        expenditure = test_utils.create_expenditure(
            account=self.account, amount=Decimal("100")
        ).amount

        result = utils.generate_reports(user=self.account.owner)

        reports = test_utils.create_empty_reports(last_date=self.now)
        reports.append(
            {
                "month": self.now.month,
                "year": self.now.year,
                "income": income,
                "expenditures": expenditure,
                "balance": income - expenditure,
            }
        )

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": self.account.currency,
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_reports_for_multiple_months(self):

        income_current_month = test_utils.create_income(
            account=self.account, amount=Decimal("310.15")
        ).amount

        expenditure_current_month = test_utils.create_expenditure(
            account=self.account, amount=Decimal("100.10")
        ).amount

        first_day_of_the_current_month = self.now.replace(day=1)
        one_month_ago = first_day_of_the_current_month - relativedelta(months=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = one_month_ago
            income_one_month_ago = test_utils.create_income(
                account=self.account, amount=Decimal("412.20")
            ).amount

            expenditure_one_month_ago = test_utils.create_expenditure(
                account=self.account, amount=Decimal("111.50")
            ).amount

        two_months_ago = one_month_ago - relativedelta(months=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = two_months_ago
            income_two_months_ago = test_utils.create_income(
                account=self.account, amount=Decimal("65.43")
            ).amount

            expenditure_two_months_ago = test_utils.create_expenditure(
                account=self.account, amount=Decimal("11.32")
            ).amount

        result = utils.generate_reports(user=self.account.owner)

        reports = []
        for count in reversed(range(3, 6)):
            date = self.now - relativedelta(months=count)
            reports.append(
                {
                    "month": date.month,
                    "year": date.year,
                    "income": 0,
                    "expenditures": 0,
                    "balance": 0,
                }
            )

        report_two_months_ago = {
            "month": two_months_ago.month,
            "year": two_months_ago.year,
            "income": income_two_months_ago,
            "expenditures": expenditure_two_months_ago,
            "balance": income_two_months_ago - expenditure_two_months_ago,
        }

        report_one_month_ago = {
            "month": one_month_ago.month,
            "year": one_month_ago.year,
            "income": income_one_month_ago,
            "expenditures": expenditure_one_month_ago,
            "balance": report_two_months_ago["balance"]
            + income_one_month_ago
            - expenditure_one_month_ago,
        }

        report_current_month = {
            "month": self.now.month,
            "year": self.now.year,
            "income": income_current_month,
            "expenditures": expenditure_current_month,
            "balance": report_one_month_ago["balance"]
            + income_current_month
            - expenditure_current_month,
        }

        reports.extend(
            [report_two_months_ago, report_one_month_ago, report_current_month]
        )

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": self.account.currency,
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_reports_for_multiple_months_with_start_date(self):

        income_current_month = test_utils.create_income(
            account=self.account, amount=Decimal("310.15")
        ).amount

        expenditure_current_month = test_utils.create_expenditure(
            account=self.account, amount=Decimal("100.10")
        ).amount

        first_day_of_the_current_month = self.now.replace(day=1)
        one_month_ago = first_day_of_the_current_month - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = one_month_ago
            income_one_month_ago = test_utils.create_income(
                account=self.account, amount=Decimal("412.20")
            ).amount

            expenditure_one_month_ago = test_utils.create_expenditure(
                account=self.account, amount=Decimal("111.50")
            ).amount

        first_day_of_the_last_month = one_month_ago.replace(day=1)
        two_months_ago = first_day_of_the_last_month - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = two_months_ago
            income_two_months_ago = test_utils.create_income(
                account=self.account, amount=Decimal("65.43")
            ).amount

            expenditure_two_months_ago = test_utils.create_expenditure(
                account=self.account, amount=Decimal("11.32")
            ).amount

        result = utils.generate_reports(self.account.owner, first_day_of_the_last_month)

        starting_balance = income_two_months_ago - expenditure_two_months_ago

        report_one_month_ago = {
            "month": one_month_ago.month,
            "year": one_month_ago.year,
            "income": income_one_month_ago,
            "expenditures": expenditure_one_month_ago,
            "balance": starting_balance
            + income_one_month_ago
            - expenditure_one_month_ago,
        }

        report_current_month = {
            "month": self.now.month,
            "year": self.now.year,
            "income": income_current_month,
            "expenditures": expenditure_current_month,
            "balance": report_one_month_ago["balance"]
            + income_current_month
            - expenditure_current_month,
        }

        reports = [report_one_month_ago, report_current_month]

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": self.account.currency,
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)
