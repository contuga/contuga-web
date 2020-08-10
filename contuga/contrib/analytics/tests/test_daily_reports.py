from datetime import timedelta
from decimal import Decimal
from unittest import mock

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils import timezone

from contuga.mixins import TestMixin

from .. import utils
from ..constants import DAYS
from . import utils as test_utils


class DailyReportsTestCase(TestCase, TestMixin):
    def setUp(self):
        self.now = timezone.now().astimezone()
        self.user = self.create_user(email="john.doe@example.com", password="password")
        self.account = self.create_account()

    def test_report_with_single_account(self):
        income = self.create_income(amount=Decimal("310")).amount

        expenditure = self.create_expenditure(amount=Decimal("100")).amount

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
        first_account_income = self.create_income(amount=Decimal("310.40")).amount

        first_account_expenditure = self.create_expenditure(
            amount=Decimal("100.50")
        ).amount

        second_account = self.create_account(name="Second account name")

        second_account_income = self.create_income(
            account=second_account, amount=Decimal("1034.44")
        ).amount

        second_account_expenditure = self.create_expenditure(
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
        expenditure = self.create_expenditure(amount=Decimal("100.50")).amount

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
        income = self.create_income(amount=Decimal("310.40")).amount

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
        first_income = self.create_income(amount=Decimal("310.40")).amount

        second_income = self.create_income(amount=Decimal("310.40")).amount

        first_expenditure = self.create_expenditure(amount=Decimal("100.50")).amount

        second_expenditure = self.create_expenditure(amount=Decimal("100.50")).amount

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
        self.create_account(name="Second account name")

        income = self.create_income(amount=Decimal("310")).amount

        expenditure = self.create_expenditure(amount=Decimal("100")).amount

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

        income_today = self.create_income(amount=Decimal("310.15")).amount

        expenditure_today = self.create_expenditure(amount=Decimal("100.10")).amount

        yesterday = self.now - relativedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = yesterday
            income_yesterday = self.create_income(amount=Decimal("412.20")).amount

            expenditure_yesterday = self.create_expenditure(
                amount=Decimal("111.50")
            ).amount

        two_days_ago = self.now - relativedelta(days=2)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = two_days_ago
            income_two_days_ago = self.create_income(amount=Decimal("65.43")).amount

            expenditure_two_days_ago = self.create_expenditure(
                amount=Decimal("11.32")
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

        income_today = self.create_income(amount=Decimal("310.15")).amount

        expenditure_today = self.create_expenditure(amount=Decimal("100.10")).amount

        yesterday = self.now - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = yesterday
            income_yesterday = self.create_income(amount=Decimal("412.20")).amount

            expenditure_yesterday = self.create_expenditure(
                amount=Decimal("111.50")
            ).amount

        two_days_ago = self.now - timedelta(days=2)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = two_days_ago
            income_two_days_ago = self.create_income(amount=Decimal("65.43")).amount

            expenditure_two_days_ago = self.create_expenditure(
                amount=Decimal("11.32")
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

    def test_reports_for_multiple_days_with_end_date(self):
        self.create_income(amount=Decimal("310.15")).amount

        self.create_expenditure(amount=Decimal("100.10")).amount

        yesterday = self.now - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = yesterday
            income_yesterday = self.create_income(amount=Decimal("412.20")).amount

            expenditure_yesterday = self.create_expenditure(
                amount=Decimal("111.50")
            ).amount

        two_days_ago = self.now - timedelta(days=2)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = two_days_ago
            income_two_days_ago = self.create_income(amount=Decimal("65.43")).amount

            expenditure_two_days_ago = self.create_expenditure(
                amount=Decimal("11.32")
            ).amount

        with self.assertNumQueries(1):
            result = utils.generate_reports(
                user=self.account.owner, end_date=yesterday, report_unit=DAYS
            )

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

        reports.extend([report_two_days_ago, report_yesterday])

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": self.account.currency,
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_reports_for_multiple_days_with_start_and_end_date(self):
        self.create_income(amount=Decimal("310.15")).amount
        self.create_expenditure(amount=Decimal("100.10")).amount

        yesterday = self.now - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = yesterday
            income_yesterday = self.create_income(amount=Decimal("412.20")).amount

            expenditure_yesterday = self.create_expenditure(
                amount=Decimal("111.50")
            ).amount

        two_days_ago = self.now - timedelta(days=2)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = two_days_ago
            income_two_days_ago = self.create_income(amount=Decimal("65.43")).amount

            expenditure_two_days_ago = self.create_expenditure(
                amount=Decimal("11.32")
            ).amount

        with self.assertNumQueries(1):
            result = utils.generate_reports(
                user=self.account.owner,
                start_date=yesterday,
                end_date=yesterday,
                report_unit=DAYS,
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

        reports = [report_yesterday]

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": self.account.currency,
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)
