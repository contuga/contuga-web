import json
from datetime import date, timedelta
from decimal import Decimal
from unittest import mock

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from contuga.mixins import TestMixin

from .. import constants, utils


class AnalyticsTestCase(TestCase, TestMixin):
    def setUp(self):
        self.user = self.create_user(email="john.doe@example.com", password="password")
        self.currency = self.create_currency()
        self.account = self.create_account()
        self.client.force_login(self.user)

    def test_get_monthly_reports_without_query_params(self):
        self.create_income(amount=Decimal("310"))

        self.create_expenditure(amount=Decimal("100"))

        url = reverse("analytics:list")
        response = self.client.get(url, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.MONTHS
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        unit_field = form.fields["report_unit"]
        self.assertEqual(unit_field.initial, constants.MONTHS)

    def test_get_monthly_reports_with_unit(self):
        self.create_income(amount=Decimal("310"))

        self.create_expenditure(amount=Decimal("100"))

        url = reverse("analytics:list")
        response = self.client.get(url, {"report_unit": constants.MONTHS}, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.MONTHS
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        self.assertEqual(
            form.cleaned_data,
            {"report_unit": constants.MONTHS, "start_date": None, "end_date": None},
        )

    def test_get_monthly_reports_with_invalid_unit(self):
        self.create_income(amount=Decimal("310"))

        self.create_expenditure(amount=Decimal("100"))

        url = reverse("analytics:list")
        response = self.client.get(
            url, {"report_unit": "INVALID_REPORT_UNIT"}, follow=True
        )

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(user=self.account.owner)
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is invalid
        form = response.context.get("form")
        self.assertFalse(form.is_valid())

    def test_get_monthly_reports_with_start_date(self):
        self.create_income(amount=Decimal("310"))

        self.create_expenditure(amount=Decimal("100"))

        url = reverse("analytics:list")
        today = timezone.now().astimezone().date()
        date_string = today.strftime("%m/%d/%Y")
        response = self.client.get(url, {"start_date": date_string}, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.MONTHS, start_date=today
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        self.assertEqual(
            form.cleaned_data,
            {"report_unit": constants.MONTHS, "start_date": today, "end_date": None},
        )

    def test_get_monthly_reports_with_invalid_start_date(self):
        self.create_income(amount=Decimal("310"))

        self.create_expenditure(amount=Decimal("100"))

        url = reverse("analytics:list")
        response = self.client.get(
            url, {"start_date": "INVALID_START_DATE"}, follow=True
        )

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.MONTHS
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {"start_date": [_("Enter a valid date.")]})

    def test_get_monthly_reports_with_start_date_before_2019(self):
        self.create_income(amount=Decimal("310"))

        self.create_expenditure(amount=Decimal("100"))

        url = reverse("analytics:list")
        response = self.client.get(
            url, {"start_date": date(year=2018, month=12, day=31)}, follow=True
        )

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.MONTHS
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors, {"start_date": [_("The start date cannot be before 2019.")]}
        )

    def test_get_monthly_reports_with_end_date(self):
        self.create_income(amount=Decimal("310"))
        self.create_expenditure(amount=Decimal("100"))

        first_day_of_the_current_month = timezone.now().astimezone().replace(day=1)
        one_month_ago = first_day_of_the_current_month - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = one_month_ago
            self.create_income(amount=Decimal("412.20")).amount

            self.create_expenditure(amount=Decimal("111.50")).amount

        url = reverse("analytics:list")
        date_string = one_month_ago.strftime("%m/%d/%Y")
        response = self.client.get(url, {"end_date": date_string}, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner,
            report_unit=constants.MONTHS,
            end_date=one_month_ago.date(),
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        self.assertEqual(
            form.cleaned_data,
            {
                "report_unit": constants.MONTHS,
                "start_date": None,
                "end_date": one_month_ago.date(),
            },
        )

    def test_get_monthly_reports_with_end_date_before_2019(self):
        self.create_income(amount=Decimal("310"))
        self.create_expenditure(amount=Decimal("100"))

        url = reverse("analytics:list")
        response = self.client.get(
            url, {"end_date": date(year=2018, month=12, day=31)}, follow=True
        )

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.MONTHS
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors, {"end_date": [_("The end date cannot be before 2019.")]}
        )

    def test_get_monthly_reports_with_end_date_in_the_future(self):
        self.create_income(amount=Decimal("310"))
        self.create_expenditure(amount=Decimal("100"))

        tomorow = timezone.now().astimezone() + timedelta(days=1)

        date_string = tomorow.strftime("%m/%d/%Y")
        url = reverse("analytics:list")
        response = self.client.get(url, {"end_date": date_string}, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.MONTHS
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors, {"end_date": [_("The end date cannot be in the future.")]}
        )

    def test_get_monthly_reports_with_start_and_end_date(self):
        self.create_income(amount=Decimal("310"))
        self.create_expenditure(amount=Decimal("100"))

        first_day_of_the_current_month = timezone.now().astimezone().replace(day=1)
        one_month_ago = first_day_of_the_current_month - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = one_month_ago
            self.create_income(amount=Decimal("412.20")).amount

            self.create_expenditure(amount=Decimal("111.50")).amount

        url = reverse("analytics:list")
        date_string = one_month_ago.strftime("%m/%d/%Y")
        response = self.client.get(
            url, {"start_date": date_string, "end_date": date_string}, follow=True
        )

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner,
            report_unit=constants.MONTHS,
            start_date=one_month_ago.date(),
            end_date=one_month_ago.date(),
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        self.assertEqual(
            form.cleaned_data,
            {
                "report_unit": constants.MONTHS,
                "start_date": one_month_ago.date(),
                "end_date": one_month_ago.date(),
            },
        )

    def test_get_daily_reports(self):
        self.create_income(amount=Decimal("310"))

        self.create_expenditure(amount=Decimal("100"))

        url = reverse("analytics:list")
        response = self.client.get(url, {"report_unit": constants.DAYS}, follow=True)

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.DAYS
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        self.assertEqual(
            form.cleaned_data,
            {"report_unit": constants.DAYS, "start_date": None, "end_date": None},
        )

    def test_get_daily_reports_with_start_date(self):
        self.create_income(amount=Decimal("310"))

        self.create_expenditure(amount=Decimal("100"))

        url = reverse("analytics:list")
        today = timezone.now().astimezone().date()
        date_string = today.strftime("%m/%d/%Y")
        response = self.client.get(
            url, {"report_unit": constants.DAYS, "start_date": date_string}, follow=True
        )

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner, report_unit=constants.DAYS, start_date=today
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        self.assertEqual(
            form.cleaned_data,
            {"report_unit": constants.DAYS, "start_date": today, "end_date": None},
        )

    def test_get_daily_reports_with_end_date(self):
        self.create_income(amount=Decimal("310"))
        self.create_expenditure(amount=Decimal("100"))

        yesterday = timezone.now().astimezone() - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = yesterday
            self.create_income(amount=Decimal("412.20")).amount

            self.create_expenditure(amount=Decimal("111.50")).amount

        url = reverse("analytics:list")
        date_string = yesterday.strftime("%m/%d/%Y")
        response = self.client.get(
            url, {"report_unit": constants.DAYS, "end_date": date_string}, follow=True
        )

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner,
            report_unit=constants.DAYS,
            end_date=yesterday.date(),
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        self.assertEqual(
            form.cleaned_data,
            {
                "report_unit": constants.DAYS,
                "start_date": None,
                "end_date": yesterday.date(),
            },
        )

    def test_get_daily_reports_with_start_and_end_date(self):
        self.create_income(amount=Decimal("310"))
        self.create_expenditure(amount=Decimal("100"))

        yesterday = timezone.now().astimezone() - timedelta(days=1)

        with mock.patch("django.utils.timezone.now") as mocked_now:
            mocked_now.return_value = yesterday
            self.create_income(amount=Decimal("412.20")).amount

            self.create_expenditure(amount=Decimal("111.50")).amount

        url = reverse("analytics:list")
        date_string = yesterday.strftime("%m/%d/%Y")
        response = self.client.get(
            url,
            {
                "report_unit": constants.DAYS,
                "start_date": date_string,
                "end_date": date_string,
            },
            follow=True,
        )

        # Assert status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert reports are correct
        expected_reports = utils.generate_reports(
            user=self.account.owner,
            report_unit=constants.DAYS,
            start_date=yesterday.date(),
            end_date=yesterday.date(),
        )
        expected_json = json.dumps(expected_reports, cls=DjangoJSONEncoder)

        self.assertEqual(response.context["reports"], expected_json)
        self.assertContains(response=response, text=expected_json)

        # Assert form is correct
        form = response.context.get("form")
        self.assertEqual(
            form.cleaned_data,
            {
                "report_unit": constants.DAYS,
                "start_date": yesterday.date(),
                "end_date": yesterday.date(),
            },
        )
