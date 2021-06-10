import pytz
from django.db.models import DecimalField, OuterRef, Q, Subquery, Sum
from django.db.models.functions import Coalesce

from .. import constants
from .common_utils import construct_date_string


def get_accounts_data(transactions, start_date, end_date, truncClass):
    if end_date:
        # Calculte the account balance until the selected end_date
        account__balance = (
            transactions.filter(
                account__pk=OuterRef("account__pk"),
                created_at__lte=end_date.astimezone(pytz.UTC),
            )
            .annotate(created_on=truncClass("created_at", tzinfo=start_date.tzinfo))
            .values("account__pk")
            .annotate(
                balance=Coalesce(Sum("amount", filter=Q(type="income")), 0)
                - Coalesce(Sum("amount", filter=Q(type="expenditure")), 0)
            )
            .values("balance")
            .order_by()
        )

    queryset = transactions.filter(
        created_at__gte=start_date.astimezone(pytz.UTC),
        created_at__lte=end_date.astimezone(pytz.UTC),
    ).annotate(created_on=truncClass("created_at", tzinfo=start_date.tzinfo))

    values = [
        "account__name",
        "account__pk",
        "account__currency__code",
        "account__currency__name",
        "created_on",
    ]

    queryset = queryset.annotate(
        account__balance=Subquery(account__balance, output_field=DecimalField())
    )

    values.append("account__balance")

    return (
        queryset.values(*values).annotate(
            income=Coalesce(Sum("amount", filter=Q(type="income")), 0),
            expenditures=Coalesce(Sum("amount", filter=Q(type="expenditure")), 0),
        )
        # order_by() is used to remove the default ordering from Group By
        # https://docs.djangoproject.com/en/2.2/topics/db/aggregation/#interaction-with-default-ordering-or-order-by
        .order_by("account__name")
    )


def group_account_reports(aggregated_data, report_unit):
    grouped_reports = {}

    for item in aggregated_data:
        default = {
            "pk": item["account__pk"],
            "name": item["account__name"],
            "currency": {
                "code": item["account__currency__code"],
                "name": item["account__currency__name"],
            },
            "reports": {},
        }

        if item.get("account__balance"):
            default["balance"] = item["account__balance"]

        account = grouped_reports.setdefault(item["account__pk"], default)

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

        account["reports"][key] = report

    return list(grouped_reports.values())
