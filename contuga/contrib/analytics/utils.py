from datetime import datetime, time

from dateutil.relativedelta import relativedelta
import pytz

from django.db.models import Sum, Q
from django.db.models.functions import Coalesce, TruncDay, TruncMonth
from django.utils import timezone
from django.conf import settings

from contuga.contrib.transactions.models import Transaction
from .constants import DAYS, MONTHS


REPORTS = {
    MONTHS: {"default_period": {"months": 5}, "truncClass": TruncMonth},
    DAYS: {"default_period": {"months": 1}, "truncClass": TruncDay},
}


def get_aggregated_data(transactions, start_date, end_date, truncClass):
    return (
        transactions.filter(
            created_at__gte=start_date.astimezone(pytz.UTC),
            created_at__lte=end_date.astimezone(pytz.UTC),
        )
        .annotate(created_on=truncClass("created_at", tzinfo=start_date.tzinfo))
        .values(
            "account__name",
            "account__pk",
            "account__balance",
            "account__currency",
            "created_on",
        )
        .annotate(
            income=Coalesce(Sum("amount", filter=Q(type="income")), 0),
            expenditures=Coalesce(Sum("amount", filter=Q(type="expenditure")), 0),
        )
        # order_by() is used to remove the default ordering from Group By
        # https://docs.djangoproject.com/en/2.2/topics/db/aggregation/#interaction-with-default-ordering-or-order-by
        .order_by()
    )


def construct_date_string(year, month, day=None):
    if day:
        return f"{year}{str(month).zfill(2)}{str(day).zfill(2)}"
    else:
        return f"{year}{str(month).zfill(2)}"


def group_reports(aggregated_data, report_unit):
    grouped_reports = {}

    for item in aggregated_data:
        account = grouped_reports.setdefault(
            item["account__pk"],
            {
                "pk": item["account__pk"],
                "name": item["account__name"],
                "currency": item["account__currency"],
                "balance": item["account__balance"],
                "reports": {},
            },
        )

        year = item["created_on"].year
        month = item["created_on"].month

        report = {
            "month": month,
            "year": year,
            "income": item["income"],
            "expenditures": item["expenditures"],
        }

        if report_unit == DAYS:
            day = item["created_on"].day
            key = construct_date_string(year, month, day)
            report["day"] = day
        else:
            key = construct_date_string(year, month)

        account["reports"][key] = report

    return list(grouped_reports.values())


def calculate_balance(report, next_report, account_balance, today):
    if (
        report["year"] == today.year
        and report["month"] == today.month
        and report.get("day", today.day) == today.day
    ):
        return account_balance
    else:
        return (
            next_report.get("balance", 0)
            - next_report.get("income", 0)
            + next_report.get("expenditures", 0)
        )


def process_monthly_reports(reports, start_date):
    start_date_string = construct_date_string(start_date.year, start_date.month)

    for account in reports:
        today = timezone.now().astimezone().date()
        year = today.year
        month = today.month

        date_string = construct_date_string(year, month)
        next_date = date_string

        while date_string >= start_date_string:
            report = account["reports"].setdefault(
                date_string,
                {"month": month, "year": year, "income": 0, "expenditures": 0},
            )

            report["balance"] = calculate_balance(
                report=report,
                next_report=account["reports"][next_date],
                account_balance=account["balance"],
                today=today,
            )

            next_date = date_string

            month -= 1

            if month <= 0:
                year -= 1
                month = 12

            date_string = construct_date_string(year, month)

        del account["balance"]

        account["reports"] = sorted(
            account["reports"].values(), key=lambda x: (x["year"], x["month"])
        )

    return reports


def process_daily_reports(reports, start_date):
    start_date_string = construct_date_string(
        start_date.year, start_date.month, start_date.day
    )

    for account in reports:
        today = timezone.now().astimezone().date()
        date = timezone.now().astimezone().date()
        date_string = construct_date_string(date.year, date.month, date.day)
        next_date = date_string

        while date_string >= start_date_string:
            report = account["reports"].setdefault(
                date_string,
                {
                    "month": date.month,
                    "year": date.year,
                    "day": date.day,
                    "income": 0,
                    "expenditures": 0,
                },
            )

            report["balance"] = calculate_balance(
                report=report,
                next_report=account["reports"][next_date],
                account_balance=account["balance"],
                today=today,
            )

            next_date = date_string

            date = date - relativedelta(days=1)

            date_string = construct_date_string(date.year, date.month, date.day)

        del account["balance"]

        account["reports"] = sorted(
            account["reports"].values(), key=lambda x: (x["year"], x["month"], x["day"])
        )

    return reports


def process_reports(reports, report_unit, start_date):
    if report_unit == DAYS:
        return process_daily_reports(reports=reports, start_date=start_date)
    else:
        return process_monthly_reports(reports=reports, start_date=start_date)


def generate_reports(user, start_date=None, end_date=None, report_unit=MONTHS):
    transactions = Transaction.objects.filter(account__is_active=True, author=user)

    # If empty_string is passed as report_unit
    if not report_unit:
        report_unit = MONTHS

    conf = REPORTS[report_unit]

    today = timezone.now().astimezone().date()
    if not start_date:
        start_date = today - relativedelta(**conf["default_period"])
    if not end_date:
        end_date = today

    # TODO: Let users specify their timezone and use it below
    tzinfo = pytz.timezone(settings.TIME_ZONE)

    start_date = datetime.combine(date=start_date, time=time.min, tzinfo=tzinfo)
    end_date = datetime.combine(date=end_date, time=time.max, tzinfo=tzinfo)

    aggregated_data = get_aggregated_data(
        transactions=transactions,
        start_date=start_date,
        end_date=end_date,
        truncClass=conf["truncClass"],
    )
    grouped_reports = group_reports(aggregated_data, report_unit=report_unit)
    processed_reports = process_reports(
        reports=grouped_reports, start_date=start_date, report_unit=report_unit
    )

    return processed_reports
