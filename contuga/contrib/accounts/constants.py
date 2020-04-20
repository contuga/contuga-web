from django.utils.translation import ugettext_lazy as _

BGN = "BGN"
EUR = "EUR"
USD = "USD"
GBP = "GBP"
CHF = "CHF"
RUB = "RUB"
CNY = "CNY"

CURRENCY_CHOICES = (
    (BGN, _("Bulgarian lev")),
    (EUR, _("Euro")),
    (USD, _("US Dollars")),
    (GBP, _("British pound")),
    (CHF, _("Swiss franc")),
    (RUB, _("Russian ruble")),
    (CNY, _("Chinese yuan")),
)
