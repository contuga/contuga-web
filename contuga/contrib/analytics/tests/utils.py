from dateutil.relativedelta import relativedelta

from contuga.contrib.transactions import constants as transaction_constants
from contuga.contrib.transactions.models import Transaction

from ..constants import DAYS, MONTHS


def create_income(account, amount):
    return Transaction.objects.create(
        type=transaction_constants.INCOME,
        amount=amount,
        author=account.owner,
        account=account,
    )


def create_expenditure(account, amount):
    return Transaction.objects.create(
        type=transaction_constants.EXPENDITURE,
        amount=amount,
        author=account.owner,
        account=account,
    )


def create_empty_reports(last_date, report_unit=MONTHS):
    reports = []

    if report_unit == MONTHS:
        range_end = 6
    else:
        range_end = (last_date - (last_date - relativedelta(months=1))).days + 1

    for i in reversed(range(1, range_end)):
        if report_unit == MONTHS:
            date = last_date - relativedelta(months=i)
        else:
            date = last_date - relativedelta(days=i)

        report = {
            "month": date.month,
            "year": date.year,
            "income": 0,
            "expenditures": 0,
            "balance": 0,
        }

        if report_unit == DAYS:
            report["day"] = date.day

        reports.append(report)

    return reports
