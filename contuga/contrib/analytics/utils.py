from datetime import datetime, time

from dateutil.relativedelta import relativedelta
import pytz

from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from contuga.contrib.transactions.models import Transaction


def get_aggregated_data(transactions, start_date):
    return (
        transactions.filter(created_at__gte=start_date)
        .values(
            "account__name",
            "account__pk",
            "account__balance",
            "account__currency",
            "created_at__month",
            "created_at__year",
        )
        .annotate(
            income=Coalesce(Sum("amount", filter=Q(type="income")), 0),
            expenditures=Coalesce(Sum("amount", filter=Q(type="expenditure")), 0),
        )
        # order_by() is used to remove the default ordering from Group By
        # https://docs.djangoproject.com/en/2.2/topics/db/aggregation/#interaction-with-default-ordering-or-order-by
        .order_by()
    )


def group_reports(aggregated_data):
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

        year = item["created_at__year"]
        month = item["created_at__month"]

        account["reports"][f"{year}{str(month).zfill(2)}"] = {
            "month": item["created_at__month"],
            "year": item["created_at__year"],
            "income": item["income"],
            "expenditures": item["expenditures"],
        }
    return grouped_reports


def calculate_balance(report, next_report, account_balance, today):
    if report["year"] == today.year and report["month"] == today.month:
        return account_balance
    else:
        return (
            next_report.get("balance", 0)
            - next_report.get("income", 0)
            + next_report.get("expenditures", 0)
        )


def process_reports(start_date, grouped_reports):
    start_date_string = f"{start_date.year}{str(start_date.month).zfill(2)}"

    for primary_key, account in grouped_reports.items():
        today = timezone.now().astimezone().date()
        year = today.year
        month = today.month
        date_string = f"{year}{str(month).zfill(2)}"
        next_month = date_string

        while date_string >= start_date_string:
            report = account["reports"].setdefault(
                date_string,
                {"month": month, "year": year, "income": 0, "expenditures": 0},
            )

            report["balance"] = calculate_balance(
                report=report,
                next_report=account["reports"][next_month],
                account_balance=account["balance"],
                today=today
            )

            next_month = date_string

            month -= 1

            if month <= 0:
                year -= 1
                month = 12

            date_string = f"{year}{str(month).zfill(2)}"

        del account["balance"]

        account["reports"] = sorted(
            account["reports"].values(), key=lambda x: (x["year"], x["month"])
        )

    return grouped_reports


def get_monthly_reports(user, start_date=None):
    transactions = Transaction.objects.filter(account__is_active=True, author=user)

    if not start_date:
        start_date = timezone.now().astimezone().date() - relativedelta(months=6)

    start_date = datetime.combine(date=start_date, time=time.min, tzinfo=pytz.UTC)

    aggregated_data = get_aggregated_data(transactions, start_date)
    grouped_reports = group_reports(aggregated_data)
    processed_reports = process_reports(start_date, grouped_reports)

    return list(processed_reports.values())
