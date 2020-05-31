from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from contuga.contrib.accounts import constants as account_constants
from contuga.contrib.accounts.models import Account

from .. import constants, utils
from . import utils as test_utils

UserModel = get_user_model()


class AnalyticsAPITestCase(APITestCase):
    def setUp(self):
        self.now = timezone.now().astimezone()
        user = UserModel.objects.create_user(
            email="john.doe@example.com", password="password"
        )
        self.account = Account.objects.create(
            name="Account name", currency=account_constants.BGN, owner=user
        )

        token, created = Token.objects.get_or_create(user=user)
        self.client = APIClient(HTTP_AUTHORIZATION="Token " + token.key)

    def test_get_monthly_reports(self):
        test_utils.create_income(account=self.account, amount=Decimal("310"))

        test_utils.create_expenditure(account=self.account, amount=Decimal("100"))

        url = reverse("analytics-list")
        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.MONTHS
        )

        expected_response = {
            "count": len(expected_reports),
            "next": None,
            "previous": None,
            "results": [
                {
                    "pk": item.get("pk"),
                    "name": item.get("name"),
                    "currency": item.get("currency"),
                    "reports": [
                        {
                            "month": report.get("month"),
                            "year": report.get("year"),
                            "income": f"{report.get('income'):.2f}",
                            "expenditures": f"{report.get('expenditures'):.2f}",
                            "balance": f"{report.get('balance'):.2f}",
                        }
                        for report in item["reports"]
                    ],
                }
                for item in expected_reports
            ],
        }
        self.assertDictEqual(response.json(), expected_response)

    def test_get_monthly_reports_with_start_date(self):
        test_utils.create_income(account=self.account, amount=Decimal("310"))

        test_utils.create_expenditure(account=self.account, amount=Decimal("100"))

        url = reverse("analytics-list")
        date_string = self.now.strftime("%m/%d/%Y")
        response = self.client.get(url, {"start_date": date_string}, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.MONTHS, start_date=self.now
        )

        expected_response = {
            "count": len(expected_reports),
            "next": None,
            "previous": None,
            "results": [
                {
                    "pk": item.get("pk"),
                    "name": item.get("name"),
                    "currency": item.get("currency"),
                    "reports": [
                        {
                            "month": report.get("month"),
                            "year": report.get("year"),
                            "income": f"{report.get('income'):.2f}",
                            "expenditures": f"{report.get('expenditures'):.2f}",
                            "balance": f"{report.get('balance'):.2f}",
                        }
                        for report in item["reports"]
                    ],
                }
                for item in expected_reports
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_get_monthly_reports_with_end_date(self):
        test_utils.create_income(account=self.account, amount=Decimal("310"))
        test_utils.create_expenditure(account=self.account, amount=Decimal("100"))

        first_day_of_the_current_month = timezone.now().astimezone().replace(day=1)
        one_month_ago = first_day_of_the_current_month - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = one_month_ago
            test_utils.create_income(
                account=self.account, amount=Decimal("412.20")
            ).amount

            test_utils.create_expenditure(
                account=self.account, amount=Decimal("111.50")
            ).amount

        url = reverse("analytics-list")
        date_string = one_month_ago.strftime("%m/%d/%Y")
        response = self.client.get(url, {"end_date": date_string}, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_reports = utils.generate_reports(
            user=self.account.owner,
            report_unit=constants.MONTHS,
            end_date=one_month_ago.date(),
        )

        expected_response = {
            "count": len(expected_reports),
            "next": None,
            "previous": None,
            "results": [
                {
                    "pk": item.get("pk"),
                    "name": item.get("name"),
                    "currency": item.get("currency"),
                    "reports": [
                        {
                            "month": report.get("month"),
                            "year": report.get("year"),
                            "income": f"{report.get('income'):.2f}",
                            "expenditures": f"{report.get('expenditures'):.2f}",
                            "balance": f"{report.get('balance'):.2f}",
                        }
                        for report in item["reports"]
                    ],
                }
                for item in expected_reports
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_get_monthly_reports_with_start_and_end_date(self):
        test_utils.create_income(account=self.account, amount=Decimal("310"))
        test_utils.create_expenditure(account=self.account, amount=Decimal("100"))

        first_day_of_the_current_month = timezone.now().astimezone().replace(day=1)
        one_month_ago = first_day_of_the_current_month - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = one_month_ago
            test_utils.create_income(
                account=self.account, amount=Decimal("412.20")
            ).amount

            test_utils.create_expenditure(
                account=self.account, amount=Decimal("111.50")
            ).amount

        url = reverse("analytics-list")
        date_string = one_month_ago.strftime("%m/%d/%Y")
        response = self.client.get(
            url, {"start_date": date_string, "end_date": date_string}, format="json"
        )

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_reports = utils.generate_reports(
            user=self.account.owner,
            report_unit=constants.MONTHS,
            start_date=one_month_ago.date(),
            end_date=one_month_ago.date(),
        )

        expected_response = {
            "count": len(expected_reports),
            "next": None,
            "previous": None,
            "results": [
                {
                    "pk": item.get("pk"),
                    "name": item.get("name"),
                    "currency": item.get("currency"),
                    "reports": [
                        {
                            "month": report.get("month"),
                            "year": report.get("year"),
                            "income": f"{report.get('income'):.2f}",
                            "expenditures": f"{report.get('expenditures'):.2f}",
                            "balance": f"{report.get('balance'):.2f}",
                        }
                        for report in item["reports"]
                    ],
                }
                for item in expected_reports
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_get_daily_reports(self):
        test_utils.create_income(account=self.account, amount=Decimal("310"))

        test_utils.create_expenditure(account=self.account, amount=Decimal("100"))

        url = reverse("analytics-list")
        response = self.client.get(url, {"report_unit": constants.DAYS}, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.DAYS
        )

        expected_response = {
            "count": len(expected_reports),
            "next": None,
            "previous": None,
            "results": [
                {
                    "pk": item.get("pk"),
                    "name": item.get("name"),
                    "currency": item.get("currency"),
                    "reports": [
                        {
                            "day": report.get("day"),
                            "month": report.get("month"),
                            "year": report.get("year"),
                            "income": f"{report.get('income'):.2f}",
                            "expenditures": f"{report.get('expenditures'):.2f}",
                            "balance": f"{report.get('balance'):.2f}",
                        }
                        for report in item["reports"]
                    ],
                }
                for item in expected_reports
            ],
        }
        self.assertDictEqual(response.json(), expected_response)

    def test_get_daily_reports_with_start_date(self):
        test_utils.create_income(account=self.account, amount=Decimal("310"))

        test_utils.create_expenditure(account=self.account, amount=Decimal("100"))

        url = reverse("analytics-list")
        date_string = self.now.strftime("%m/%d/%Y")
        response = self.client.get(
            url,
            {"report_unit": constants.DAYS, "start_date": date_string},
            format="json",
        )

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.DAYS, start_date=self.now
        )

        expected_response = {
            "count": len(expected_reports),
            "next": None,
            "previous": None,
            "results": [
                {
                    "pk": item.get("pk"),
                    "name": item.get("name"),
                    "currency": item.get("currency"),
                    "reports": [
                        {
                            "day": report.get("day"),
                            "month": report.get("month"),
                            "year": report.get("year"),
                            "income": f"{report.get('income'):.2f}",
                            "expenditures": f"{report.get('expenditures'):.2f}",
                            "balance": f"{report.get('balance'):.2f}",
                        }
                        for report in item["reports"]
                    ],
                }
                for item in expected_reports
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_get_daily_reports_with_end_date(self):
        test_utils.create_income(account=self.account, amount=Decimal("310"))
        test_utils.create_expenditure(account=self.account, amount=Decimal("100"))

        yesterday = self.now - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = yesterday
            test_utils.create_income(
                account=self.account, amount=Decimal("412.20")
            ).amount

            test_utils.create_expenditure(
                account=self.account, amount=Decimal("111.50")
            ).amount

        url = reverse("analytics-list")
        date_string = yesterday.strftime("%m/%d/%Y")
        response = self.client.get(
            url, {"report_unit": constants.DAYS, "end_date": date_string}, format="json"
        )

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_reports = utils.generate_reports(
            user=self.account.owner,
            report_unit=constants.DAYS,
            end_date=yesterday.date(),
        )

        expected_response = {
            "count": len(expected_reports),
            "next": None,
            "previous": None,
            "results": [
                {
                    "pk": item.get("pk"),
                    "name": item.get("name"),
                    "currency": item.get("currency"),
                    "reports": [
                        {
                            "day": report.get("day"),
                            "month": report.get("month"),
                            "year": report.get("year"),
                            "income": f"{report.get('income'):.2f}",
                            "expenditures": f"{report.get('expenditures'):.2f}",
                            "balance": f"{report.get('balance'):.2f}",
                        }
                        for report in item["reports"]
                    ],
                }
                for item in expected_reports
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_get_daily_reports_with_start_and_end_date(self):
        test_utils.create_income(account=self.account, amount=Decimal("310"))
        test_utils.create_expenditure(account=self.account, amount=Decimal("100"))

        yesterday = self.now - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = yesterday
            test_utils.create_income(
                account=self.account, amount=Decimal("412.20")
            ).amount

            test_utils.create_expenditure(
                account=self.account, amount=Decimal("111.50")
            ).amount

        url = reverse("analytics-list")
        date_string = yesterday.strftime("%m/%d/%Y")
        response = self.client.get(
            url,
            {
                "report_unit": constants.DAYS,
                "start_date": date_string,
                "end_date": date_string,
            },
            format="json",
        )

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        expected_reports = utils.generate_reports(
            user=self.account.owner,
            report_unit=constants.DAYS,
            start_date=yesterday.date(),
            end_date=yesterday.date(),
        )

        expected_response = {
            "count": len(expected_reports),
            "next": None,
            "previous": None,
            "results": [
                {
                    "pk": item.get("pk"),
                    "name": item.get("name"),
                    "currency": item.get("currency"),
                    "reports": [
                        {
                            "day": report.get("day"),
                            "month": report.get("month"),
                            "year": report.get("year"),
                            "income": f"{report.get('income'):.2f}",
                            "expenditures": f"{report.get('expenditures'):.2f}",
                            "balance": f"{report.get('balance'):.2f}",
                        }
                        for report in item["reports"]
                    ],
                }
                for item in expected_reports
            ],
        }

        self.assertDictEqual(response.json(), expected_response)
