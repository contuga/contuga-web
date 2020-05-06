from django import forms
from django.utils.translation import pgettext_lazy, ugettext_lazy as _
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from . import models
from contuga.contrib.accounts.models import Account
from contuga.contrib.categories.models import Category
from contuga.contrib.categories import constants as category_constants


class TransactionCreateForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ("type", "amount", "account", "category", "description")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account"].queryset = Account.objects.active(owner=user)
        self.fields["category"].queryset = Category.objects.filter(
            author=user,
            transaction_type__in=[
                category_constants.ALL,
                category_constants.EXPENDITURE,
            ],
        )


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


class InternalTransferForm(forms.Form):
    from_account = forms.ModelChoiceField(label=_("From"), queryset=None)
    to_account = forms.ModelChoiceField(
        label=pgettext_lazy("preposition, towards", "To"), queryset=None
    )
    amount = forms.DecimalField(label=_("Amount"), min_value=0)
    rate = forms.DecimalField(label=_("Exchange rate"), required=False)
    description = forms.CharField(label=_("Description"), required=False)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["from_account"].queryset = Account.objects.active(owner=user)
        self.fields["to_account"].queryset = Account.objects.active(owner=user)

    def clean(self):
        cleaned_data = super().clean()
        from_account = cleaned_data.get("from_account")
        to_account = cleaned_data.get("to_account")
        rate = cleaned_data.get("rate")

        if from_account and to_account:
            if from_account == to_account:
                self.add_error(
                    NON_FIELD_ERRORS,
                    ValidationError(
                        message=_("The two accounts shouldn't be the same."),
                        code="invalid",
                    ),
                )
            if from_account.currency != to_account.currency and not rate:
                message = _(
                    "You need to specify exchange rate if the "
                    "two accounts are of different currencies."
                )
                self.add_error(
                    NON_FIELD_ERRORS, ValidationError(message=message, code="required")
                )

        return cleaned_data
