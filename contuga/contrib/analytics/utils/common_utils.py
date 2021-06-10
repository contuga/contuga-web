from datetime import datetime, time

import pytz
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone

from .. import constants


def construct_date_string(year, month, day=None):
    if day:
        return f"{year}{str(month).zfill(2)}{str(day).zfill(2)}"
    else:
        return f"{year}{str(month).zfill(2)}"


def get_date_limits(start_date, end_date, report_unit, conf):
    today = timezone.now().astimezone().date()

    if not start_date:
        start_date = today - relativedelta(**conf["default_period"])

        if report_unit == constants.MONTHS:
            start_date = start_date.replace(day=1)
    if not end_date:
        end_date = today

    # TODO: Let users specify their timezone and use it below
    tzinfo = pytz.timezone(settings.TIME_ZONE)

    start_date = datetime.combine(date=start_date, time=time.min, tzinfo=tzinfo)
    end_date = datetime.combine(date=end_date, time=time.max, tzinfo=tzinfo)

    return start_date, end_date


def process_reports(reports, report_unit, start_date, end_date):
    if report_unit == constants.DAYS:
        return process_daily_reports(
            reports=reports, start_date=start_date, end_date=end_date
        )
    else:
        return process_monthly_reports(
            reports=reports, start_date=start_date, end_date=end_date
        )


def process_monthly_reports(reports, start_date, end_date):
    start_date_string = construct_date_string(start_date.year, start_date.month)

    for account in reports:
        year = end_date.year
        month = end_date.month

        date_string = construct_date_string(year, month)
        next_date = date_string

        while date_string >= start_date_string:
            report = account["reports"].setdefault(
                date_string,
                {"month": month, "year": year, "income": 0, "expenditures": 0},
            )

            if account.get("balance"):
                report["balance"] = calculate_balance(
                    report=report,
                    next_report=account["reports"][next_date],
                    account_balance=account["balance"],
                    end_date=end_date,
                )

            next_date = date_string

            month -= 1

            if month <= 0:
                year -= 1
                month = 12

            date_string = construct_date_string(year, month)

        if account.get("balance"):
            del account["balance"]

        account["reports"] = sorted(
            account["reports"].values(), key=lambda x: (x["year"], x["month"])
        )

    return reports


def process_daily_reports(reports, start_date, end_date):
    start_date_string = construct_date_string(
        start_date.year, start_date.month, start_date.day
    )

    for account in reports:
        date = end_date.date()
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

            if account.get("balance"):
                report["balance"] = calculate_balance(
                    report=report,
                    next_report=account["reports"][next_date],
                    account_balance=account["balance"],
                    end_date=end_date,
                )

            next_date = date_string

            date = date - relativedelta(days=1)

            date_string = construct_date_string(date.year, date.month, date.day)

        if account.get("balance"):
            del account["balance"]

        account["reports"] = sorted(
            account["reports"].values(), key=lambda x: (x["year"], x["month"], x["day"])
        )

    return reports


def calculate_balance(report, next_report, account_balance, end_date):
    if (
        report["year"] == end_date.year
        and report["month"] == end_date.month
        and report.get("day", end_date.day) == end_date.day
    ):
        return account_balance
    else:
        return (
            next_report.get("balance", 0)
            - next_report.get("income", 0)
            + next_report.get("expenditures", 0)
        )
