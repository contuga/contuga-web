from django.utils.translation import ugettext_lazy as _

INCOME = "income"
EXPENDITURE = "expenditure"

TRANSACTION_TYPE_CHOICES = ((INCOME, _("Income")), (EXPENDITURE, _("Expenditure")))
