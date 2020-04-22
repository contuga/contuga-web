from unittest import mock
from decimal import Decimal
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from contuga.contrib.accounts import constants as account_constants
from contuga.contrib.accounts.models import Account
from ..constants import DAYS
from .. import utils
from . import utils as test_utils


UserModel = get_user_model()


class DailyReportsTestCase(TestCase):
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

        with self.assertNumQueries(1):
            result = utils.generate_reports(user=self.account.owner, report_unit=DAYS)

        reports = test_utils.create_empty_reports(last_date=self.now, report_unit=DAYS)
        reports.append(
            {
                "day": self.now.day,
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

        with self.assertNumQueries(1):
            result = utils.generate_reports(user=self.account.owner, report_unit=DAYS)

        first_account_reports = test_utils.create_empty_reports(
            last_date=self.now, report_unit=DAYS
        )
        second_account_reports = first_account_reports.copy()

        first_account_reports.append(
            {
                "day": self.now.day,
                "month": self.now.month,
                "year": self.now.year,
                "income": first_account_income,
                "expenditures": first_account_expenditure,
                "balance": first_account_income - first_account_expenditure,
            }
        )

        second_account_reports.append(
            {
                "day": self.now.day,
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

        with self.assertNumQueries(1):
            result = utils.generate_reports(user=self.account.owner, report_unit=DAYS)

        reports = test_utils.create_empty_reports(last_date=self.now, report_unit=DAYS)
        reports.append(
            {
                "day": self.now.day,
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

        with self.assertNumQueries(1):
            result = utils.generate_reports(user=self.account.owner, report_unit=DAYS)

        reports = test_utils.create_empty_reports(last_date=self.now, report_unit=DAYS)
        reports.append(
            {
                "day": self.now.day,
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

        with self.assertNumQueries(1):
            result = utils.generate_reports(user=self.account.owner, report_unit=DAYS)

        reports = test_utils.create_empty_reports(last_date=self.now, report_unit=DAYS)
        reports.append(
            {
                "day": self.now.day,
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

        with self.assertNumQueries(1):
            result = utils.generate_reports(user=self.account.owner, report_unit=DAYS)

        reports = test_utils.create_empty_reports(last_date=self.now, report_unit=DAYS)
        reports.append(
            {
                "day": self.now.day,
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

        income_today = test_utils.create_income(
            account=self.account, amount=Decimal("310.15")
        ).amount

        expenditure_today = test_utils.create_expenditure(
            account=self.account, amount=Decimal("100.10")
        ).amount

        yesterday = self.now - relativedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = yesterday
            income_yesterday = test_utils.create_income(
                account=self.account, amount=Decimal("412.20")
            ).amount

            expenditure_yesterday = test_utils.create_expenditure(
                account=self.account, amount=Decimal("111.50")
            ).amount

        two_days_ago = self.now - relativedelta(days=2)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = two_days_ago
            income_two_days_ago = test_utils.create_income(
                account=self.account, amount=Decimal("65.43")
            ).amount

            expenditure_two_days_ago = test_utils.create_expenditure(
                account=self.account, amount=Decimal("11.32")
            ).amount

        with self.assertNumQueries(1):
            result = utils.generate_reports(user=self.account.owner, report_unit=DAYS)

        reports = []
        days = (self.now - (self.now - relativedelta(months=1))).days
        for count in reversed(range(3, days + 1)):
            date = self.now - relativedelta(days=count)
            reports.append(
                {
                    "day": date.day,
                    "month": date.month,
                    "year": date.year,
                    "income": 0,
                    "expenditures": 0,
                    "balance": 0,
                }
            )

        report_two_days_ago = {
            "day": two_days_ago.day,
            "month": two_days_ago.month,
            "year": two_days_ago.year,
            "income": income_two_days_ago,
            "expenditures": expenditure_two_days_ago,
            "balance": income_two_days_ago - expenditure_two_days_ago,
        }

        report_yesterday = {
            "day": yesterday.day,
            "month": yesterday.month,
            "year": yesterday.year,
            "income": income_yesterday,
            "expenditures": expenditure_yesterday,
            "balance": report_two_days_ago["balance"]
            + income_yesterday
            - expenditure_yesterday,
        }

        report_today = {
            "day": self.now.day,
            "month": self.now.month,
            "year": self.now.year,
            "income": income_today,
            "expenditures": expenditure_today,
            "balance": report_yesterday["balance"] + income_today - expenditure_today,
        }

        reports.extend([report_two_days_ago, report_yesterday, report_today])

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": self.account.currency,
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_reports_for_multiple_days_with_start_date(self):

        income_today = test_utils.create_income(
            account=self.account, amount=Decimal("310.15")
        ).amount

        expenditure_today = test_utils.create_expenditure(
            account=self.account, amount=Decimal("100.10")
        ).amount

        yesterday = self.now - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = yesterday
            income_yesterday = test_utils.create_income(
                account=self.account, amount=Decimal("412.20")
            ).amount

            expenditure_yesterday = test_utils.create_expenditure(
                account=self.account, amount=Decimal("111.50")
            ).amount

        two_days_ago = self.now - timedelta(days=2)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = two_days_ago
            income_two_days_ago = test_utils.create_income(
                account=self.account, amount=Decimal("65.43")
            ).amount

            expenditure_two_days_ago = test_utils.create_expenditure(
                account=self.account, amount=Decimal("11.32")
            ).amount

        with self.assertNumQueries(1):
            result = utils.generate_reports(
                user=self.account.owner, start_date=yesterday, report_unit=DAYS
            )

        starting_balance = income_two_days_ago - expenditure_two_days_ago

        report_yesterday = {
            "day": yesterday.day,
            "month": yesterday.month,
            "year": yesterday.year,
            "income": income_yesterday,
            "expenditures": expenditure_yesterday,
            "balance": starting_balance + income_yesterday - expenditure_yesterday,
        }

        report_today = {
            "day": self.now.day,
            "month": self.now.month,
            "year": self.now.year,
            "income": income_today,
            "expenditures": expenditure_today,
            "balance": report_yesterday["balance"] + income_today - expenditure_today,
        }

        reports = [report_yesterday, report_today]

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": self.account.currency,
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)
