from dateutil.relativedelta import relativedelta

from contuga.contrib.transactions import constants as transaction_constants
from contuga.contrib.transactions.models import Transaction


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


def create_empty_reports(last_date, months=6):
    reports = []
    for count in reversed(range(1, months + 1)):
        date = last_date - relativedelta(months=count)
        reports.append(
            {
                "month": date.month,
                "year": date.year,
                "income": 0,
                "expenditures": 0,
                "balance": 0,
            }
        )
    return reports
