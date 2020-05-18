from django.utils.translation import ugettext_lazy as _

from contuga.contrib.transactions.constants import EXPENDITURE, INCOME

ALL = "all"

TRANSACTION_TYPE_CHOICES = (
    (INCOME, _("Income")),
    (EXPENDITURE, _("Expenditure")),
    (ALL, _("All")),
)
