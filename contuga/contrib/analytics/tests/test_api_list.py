from decimal import Decimal

from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from contuga.contrib.accounts import constants as account_constants
from contuga.contrib.accounts.models import Account
from .. import utils
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

    def test_get(self):
        url = reverse("analytics-list")

        test_utils.create_income(account=self.account, amount=Decimal("310")).amount

        test_utils.create_expenditure(
            account=self.account, amount=Decimal("100")
        ).amount

        response = self.client.get(url, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        result = utils.get_monthly_reports(self.account.owner)

        expected_response = {
            "count": len(result),
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
                for item in result
            ],
        }

        self.assertDictEqual(response.json(), expected_response)

    def test_get_with_filter(self):
        url = reverse("analytics-list")

        test_utils.create_income(account=self.account, amount=Decimal("310")).amount

        test_utils.create_expenditure(
            account=self.account, amount=Decimal("100")
        ).amount

        date_string = self.now.strftime("%m/%d/%Y")

        response = self.client.get(url, {"start_date": date_string}, format="json")

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert correct data is returned
        result = utils.get_monthly_reports(user=self.account.owner, start_date=self.now)

        expected_response = {
            "count": len(result),
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
                for item in result
            ],
        }

        self.assertDictEqual(response.json(), expected_response)
