from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


class TransactionFilterForm(forms.Form):
    def clean_created_at(self):
        return self.validate_date_range("created_at")

    def clean_updated_at(self):
        return self.validate_date_range("updated_at")

    def validate_date_range(self, field_name):
        value = self.cleaned_data.get(field_name)
        if not value:
            return ""

        try:
            value.split(" - ")
        except ValueError:
            self.add_error(
                field_name,
                ValidationError(message=_("Invalid date range"), code="invalid"),
            )

        return value
