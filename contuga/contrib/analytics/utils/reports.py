from django.db.models.functions import TruncDay, TruncMonth

from contuga.contrib.transactions.models import Transaction

from .. import constants
from .account_utils import get_accounts_data, group_account_reports
from .category_utils import get_categories_data, group_category_reports
from .common_utils import get_date_limits, process_reports

REPORTS = {
    constants.MONTHS: {"default_period": {"months": 5}, "truncClass": TruncMonth},
    constants.DAYS: {"default_period": {"months": 1}, "truncClass": TruncDay},
}


def generate_reports(
    user,
    start_date=None,
    end_date=None,
    report_unit=constants.MONTHS,
    grouping=constants.ACCOUNTS,
    category=None,
):
    transactions = Transaction.objects.filter(account__is_active=True, author=user)

    # If empty_string is passed as report_unit
    if not report_unit:
        report_unit = constants.MONTHS

    conf = REPORTS[report_unit]

    start_date, end_date = get_date_limits(start_date, end_date, report_unit, conf)

    if grouping == constants.ACCOUNTS:
        aggregated_data = get_accounts_data(
            transactions=transactions,
            start_date=start_date,
            end_date=end_date,
            truncClass=conf["truncClass"],
        )
        grouped_reports = group_account_reports(
            aggregated_data, report_unit=report_unit
        )
    else:
        aggregated_data = get_categories_data(
            transactions=transactions,
            start_date=start_date,
            end_date=end_date,
            category=category,
            truncClass=conf["truncClass"],
        )

        grouped_reports = group_category_reports(
            aggregated_data, report_unit=report_unit
        )

    processed_reports = process_reports(
        reports=grouped_reports,
        start_date=start_date,
        end_date=end_date,
        report_unit=report_unit,
    )

    return processed_reports
