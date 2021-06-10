import pytz
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from .. import constants
from .common_utils import construct_date_string


def get_categories_data(transactions, start_date, end_date, category, truncClass):
    transactions = transactions.filter(category=category).annotate(
        created_on=truncClass("created_at", tzinfo=start_date.tzinfo)
    )

    values = [
        "category__name",
        "category__pk",
        "account__currency__code",
        "account__currency__name",
        "created_on",
    ]

    return (
        transactions.values(*values)
        .filter(
            created_at__gte=start_date.astimezone(pytz.UTC),
            created_at__lte=end_date.astimezone(pytz.UTC),
        )
        .annotate(
            income=Coalesce(Sum("amount", filter=Q(type="income")), 0),
            expenditures=Coalesce(Sum("amount", filter=Q(type="expenditure")), 0),
        )
        # order_by() is used to remove the default ordering from Group By
        # https://docs.djangoproject.com/en/2.2/topics/db/aggregation/#interaction-with-default-ordering-or-order-by
        .order_by("category__name")
    )


def group_category_reports(aggregated_data, report_unit):
    grouped_reports = {}

    for item in aggregated_data:
        default = {
            "pk": item["category__pk"],
            "name": item["category__name"],
            "currency": {
                "name": item["account__currency__name"],
                "code": item["account__currency__code"],
            },
            "reports": {},
        }
        currency = item["account__currency__code"]
        pk = item["category__pk"]

        account = grouped_reports.setdefault(f"{pk}-{currency}", default)

        year = item["created_on"].year
        month = item["created_on"].month

        report = {
            "month": month,
            "year": year,
            "income": item["income"],
            "expenditures": item["expenditures"],
        }

        if report_unit == constants.DAYS:
            day = item["created_on"].day
            key = construct_date_string(year, month, day)
            report["day"] = day
        else:
            key = construct_date_string(year, month)

        # if not account["reports"].get(currency):
        #     account["reports"][currency] = {}

        account["reports"][key] = report

    return list(grouped_reports.values())
