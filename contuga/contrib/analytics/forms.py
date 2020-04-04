from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .constants import REPORT_UNIT_CHOICES, MONTHS


class ReportsFilterForm(forms.Form):
    report_unit = forms.ChoiceField(
        label=_("Report unit"),
        choices=(REPORT_UNIT_CHOICES),
        initial=MONTHS,
        required=False,
    )
    start_date = forms.DateField(label=_("Start date"), required=False)

    def clean_start_date(self):
        start_date = self.cleaned_data.get("start_date")

        # The project started in January 2019 and it is impossible to have earlier transactions.
        min_date = date(year=2019, month=1, day=1)
        if start_date and start_date < min_date:
            self.add_error(
                "start_date",
                ValidationError(
                    message=_("The start date cannot be before 2019."), code="invalid"
                ),
            )
        else:
            return start_date
