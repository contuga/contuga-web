from django.utils.translation import ugettext_lazy as _

DAYS = "days"
MONTHS = "months"

REPORT_UNIT_CHOICES = ((DAYS, _("Days")), (MONTHS, _("Months")))

ACCOUNTS = "accounts"
CATEGORIES = "categories"

GROUPING_CHOICES = (
    (ACCOUNTS, _("Accounts")),
    (CATEGORIES, _("Categories")),
)
