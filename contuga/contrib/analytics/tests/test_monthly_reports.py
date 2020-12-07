from datetime import timedelta
from decimal import Decimal
from unittest import mock

from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils import timezone

from contuga.mixins import TestMixin

from .. import utils
from . import utils as test_utils


class MonthlyReportsTestCase(TestCase, TestMixin):
    def setUp(self):
        self.now = timezone.now().astimezone()
        self.user = self.create_user(email="john.doe@example.com", password="password")
        self.currency = self.create_currency()
        self.account = self.create_account()

    def test_report_with_single_account(self):
        income = self.create_income(amount=Decimal("310")).amount

        expenditure = self.create_expenditure(amount=Decimal("100")).amount

        with self.assertNumQueries(1):
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
                "currency": {
                    "name": self.account.currency.name,
                    "code": self.account.currency.code,
                },
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_report_with_multiple_accounts(self):
        first_account_income = self.create_income(amount=Decimal("310.40")).amount

        first_account_expenditure = self.create_expenditure(
            amount=Decimal("100.50")
        ).amount

        second_account = self.create_account(name="Second Account Name")

        second_account_income = self.create_income(
            account=second_account, amount=Decimal("1034.44")
        ).amount

        second_account_expenditure = self.create_expenditure(
            account=second_account, amount=Decimal("833.25")
        ).amount

        with self.assertNumQueries(1):
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
                "currency": {
                    "name": self.account.currency.name,
                    "code": self.account.currency.code,
                },
                "reports": first_account_reports,
            },
            {
                "pk": second_account.pk,
                "name": second_account.name,
                "currency": {
                    "name": self.account.currency.name,
                    "code": self.account.currency.code,
                },
                "reports": second_account_reports,
            },
        ]
        self.maxDiff = None

        self.assertListEqual(result, expected_result)

    def test_report_with_no_income(self):
        expenditure = self.create_expenditure(amount=Decimal("100.50")).amount

        with self.assertNumQueries(1):
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
                "currency": {
                    "name": self.account.currency.name,
                    "code": self.account.currency.code,
                },
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_report_with_no_expenditures(self):
        income = self.create_income(amount=Decimal("310.40")).amount

        with self.assertNumQueries(1):
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
                "currency": {
                    "name": self.account.currency.name,
                    "code": self.account.currency.code,
                },
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
                "currency": {
                    "name": self.account.currency.name,
                    "code": self.account.currency.code,
                },
                "reports": reports,
            }
        ]
        self.assertListEqual(result, expected_result)

    def test_accounts_with_no_transactions_are_not_listed(self):
        self.create_account()

        income = self.create_income(amount=Decimal("310")).amount

        expenditure = self.create_expenditure(amount=Decimal("100")).amount

        with self.assertNumQueries(1):
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
                "currency": {
                    "name": self.account.currency.name,
                    "code": self.account.currency.code,
                },
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_reports_for_multiple_months(self):
        income_now = self.create_income(amount=Decimal("310.15")).amount

        expenditure_now = self.create_expenditure(amount=Decimal("100.10")).amount

        first_day_of_the_current_month = self.now.replace(day=1)
        one_month_ago = first_day_of_the_current_month - relativedelta(months=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            if self.now.day == 1:
                different_date_in_the_same_month = self.now.replace(day=10)
            else:
                different_date_in_the_same_month = first_day_of_the_current_month

            mocked_now.return_value = different_date_in_the_same_month

            income_first_day_of_current_month = self.create_income(
                amount=Decimal("20.25")
            ).amount

            expenditure_first_day_of_current_month = self.create_expenditure(
                amount=Decimal("32.50")
            ).amount

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = one_month_ago
            income_one_month_ago = self.create_income(amount=Decimal("412.20")).amount

            expenditure_one_month_ago = self.create_expenditure(
                amount=Decimal("111.50")
            ).amount

        two_months_ago = one_month_ago - relativedelta(months=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = two_months_ago
            income_two_months_ago = self.create_income(amount=Decimal("65.43")).amount

            expenditure_two_months_ago = self.create_expenditure(
                amount=Decimal("11.32")
            ).amount

        with self.assertNumQueries(1):
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

        income_current_month = income_now + income_first_day_of_current_month
        expenditure_current_month = (
            expenditure_now + expenditure_first_day_of_current_month
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
                "currency": {
                    "name": self.account.currency.name,
                    "code": self.account.currency.code,
                },
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_reports_for_multiple_months_with_start_date(self):

        income_current_month = self.create_income(amount=Decimal("310.15")).amount

        expenditure_current_month = self.create_expenditure(
            amount=Decimal("100.10")
        ).amount

        first_day_of_the_current_month = self.now.replace(day=1)
        one_month_ago = first_day_of_the_current_month - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = one_month_ago
            income_one_month_ago = self.create_income(amount=Decimal("412.20")).amount

            expenditure_one_month_ago = self.create_expenditure(
                amount=Decimal("111.50")
            ).amount

        first_day_of_the_last_month = one_month_ago.replace(day=1)
        two_months_ago = first_day_of_the_last_month - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = two_months_ago
            income_two_months_ago = self.create_income(amount=Decimal("65.43")).amount

            expenditure_two_months_ago = self.create_expenditure(
                amount=Decimal("11.32")
            ).amount

        with self.assertNumQueries(1):
            result = utils.generate_reports(
                self.account.owner, first_day_of_the_last_month
            )

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
                "currency": {
                    "name": self.account.currency.name,
                    "code": self.account.currency.code,
                },
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_reports_for_multiple_months_with_end_date(self):
        self.create_income(amount=Decimal("310.15")).amount

        self.create_expenditure(amount=Decimal("100.10")).amount

        first_day_of_the_current_month = self.now.replace(day=1)
        one_month_ago = first_day_of_the_current_month - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = one_month_ago
            income_one_month_ago = self.create_income(amount=Decimal("412.20")).amount

            expenditure_one_month_ago = self.create_expenditure(
                amount=Decimal("111.50")
            ).amount

        first_day_of_the_last_month = one_month_ago.replace(day=1)
        two_months_ago = first_day_of_the_last_month - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = two_months_ago
            income_two_months_ago = self.create_income(amount=Decimal("65.43")).amount

            expenditure_two_months_ago = self.create_expenditure(
                amount=Decimal("11.32")
            ).amount

        with self.assertNumQueries(1):
            result = utils.generate_reports(
                user=self.account.owner, end_date=one_month_ago
            )

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

        reports.extend([report_two_months_ago, report_one_month_ago])

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": {
                    "name": self.account.currency.name,
                    "code": self.account.currency.code,
                },
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_reports_for_multiple_months_with_start_and_end_date(self):
        self.create_income(amount=Decimal("310.15")).amount

        self.create_expenditure(amount=Decimal("100.10")).amount

        first_day_of_the_current_month = self.now.replace(day=1)
        one_month_ago = first_day_of_the_current_month - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = one_month_ago
            income_one_month_ago = self.create_income(amount=Decimal("412.20")).amount

            expenditure_one_month_ago = self.create_expenditure(
                amount=Decimal("111.50")
            ).amount

        first_day_of_the_last_month = one_month_ago.replace(day=1)
        two_months_ago = first_day_of_the_last_month - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = two_months_ago
            income_two_months_ago = self.create_income(amount=Decimal("65.43")).amount

            expenditure_two_months_ago = self.create_expenditure(
                amount=Decimal("11.32")
            ).amount

        with self.assertNumQueries(1):
            result = utils.generate_reports(
                user=self.account.owner,
                start_date=first_day_of_the_last_month,
                end_date=one_month_ago,
            )

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

        reports = [report_one_month_ago]

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": {
                    "name": self.account.currency.name,
                    "code": self.account.currency.code,
                },
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)

    def test_report_for_specific_category(self):
        category = self.create_category()

        income = self.create_income(amount=Decimal("310.40"), category=category).amount

        self.create_income(amount=Decimal("310.40")).amount

        expenditure = self.create_expenditure(
            amount=Decimal("100.50"), category=category
        ).amount

        self.create_expenditure(amount=Decimal("100.50")).amount

        with self.assertNumQueries(1):
            result = utils.generate_reports(user=self.account.owner, category=category)

        reports = test_utils.create_empty_reports(last_date=self.now, hasBalance=False)
        reports.append(
            {
                "month": self.now.month,
                "year": self.now.year,
                "income": income,
                "expenditures": expenditure,
            }
        )

        expected_result = [
            {
                "pk": self.account.pk,
                "name": self.account.name,
                "currency": {
                    "name": self.account.currency.name,
                    "code": self.account.currency.code,
                },
                "reports": reports,
            }
        ]

        self.assertListEqual(result, expected_result)
