from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from contuga.contrib.categories import models as category_models

from .constants import (
    ACCOUNTS,
    CHART_CHOICES,
    GROUPING_CHOICES,
    INCOME_EXPENDITURE_SIDE_BY_SIDE,
    MONTHS,
    REPORT_UNIT_CHOICES,
)


class ReportsFilterForm(forms.Form):
    report_unit = forms.ChoiceField(
        label=_("Report unit"),
        choices=REPORT_UNIT_CHOICES,
        initial=MONTHS,
        required=False,
    )
    start_date = forms.DateField(label=_("Start date"), required=False)
    end_date = forms.DateField(label=_("End date"), required=False)
    grouping = forms.ChoiceField(
        label=_("Group by"), choices=GROUPING_CHOICES, initial=ACCOUNTS, required=False
    )
    chart = forms.ChoiceField(
        label=_("Chart"),
        choices=CHART_CHOICES,
        initial=INCOME_EXPENDITURE_SIDE_BY_SIDE,
        required=False,
    )
    category = forms.ModelChoiceField(
        label=_("Category"), required=False, queryset=None
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = category_models.Category.objects.filter(
            author=user
        )

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

    def clean_end_date(self):
        end_date = self.cleaned_data.get("end_date")

        # The project started in January 2019 and it is impossible to have earlier transactions.
        min_date = date(year=2019, month=1, day=1)
        max_date = timezone.now().astimezone().date()

        if end_date and end_date > max_date:
            self.add_error(
                "end_date",
                ValidationError(
                    message=_("The end date cannot be in the future."), code="invalid"
                ),
            )
        elif end_date and end_date < min_date:
            self.add_error(
                "end_date",
                ValidationError(
                    message=_("The end date cannot be before 2019."), code="invalid"
                ),
            )
        else:
            return end_date
