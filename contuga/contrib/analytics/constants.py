from django.utils.translation import ugettext_lazy as _

DAYS = "days"
MONTHS = "months"

REPORT_UNIT_CHOICES = ((DAYS, _("Days")), (MONTHS, _("Months")))

INCOME_EXPENDITURE_SIDE_BY_SIDE = "income_expenditure_side_by_side"
INCOME_EXPENDITURE_DIFERENCE = "income_expenditure_diference"
ACCOUNT_BALANCE = "account_balance"

CHART_CHOICES = (
    (INCOME_EXPENDITURE_SIDE_BY_SIDE, _("Income and expenditure side by side")),
    (INCOME_EXPENDITURE_DIFERENCE, _("The difference between income and expenditure")),
    (ACCOUNT_BALANCE, _("Account balance")),
)

ACCOUNTS = "accounts"
CATEGORIES = "categories"

GROUPING_CHOICES = (
    (ACCOUNTS, _("Accounts")),
    (CATEGORIES, _("Categories")),
)
