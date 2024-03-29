import json

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _

from contuga.contrib.accounts.models import Account
from contuga.contrib.categories import constants as category_constants
from contuga.contrib.tags.models import Tag

from . import models


class TransactionForm(forms.ModelForm):
    # TODO: Consider using JSONField in the future.
    tags = forms.CharField(label=_("Tags"), required=False, widget=forms.Textarea)

    class Meta:
        model = models.Transaction
        fields = ("type", "amount", "account", "category", "description")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_bound and self.instance.is_part_of_transfer:
            type_field = self.fields["type"]
            type_field.disabled = True

        category_field = self.fields["category"]
        queryset = category_field.queryset.filter(author=user)

        transaction_type = self.data.get("type") if self.data else self.instance.type
        self.update_category_queryset(transaction_type, queryset)

        account_field = self.fields["account"]
        account_field.queryset = account_field.queryset.filter(
            is_active=True, owner=user
        )

    def update_category_queryset(self, type, queryset):
        category_field = self.fields["category"]

        if type == category_constants.INCOME:
            category_field.queryset = queryset.filter(
                transaction_type__in=(category_constants.ALL, category_constants.INCOME)
            )
        else:
            category_field.queryset = queryset.filter(
                transaction_type__in=(
                    category_constants.ALL,
                    category_constants.EXPENDITURE,
                )
            )

    def clean_tags(self):
        tags = self.cleaned_data.get("tags")

        if not tags:
            return []

        try:
            return json.loads(tags)
        except ValueError:
            self.add_error(
                "tags", ValidationError(message=_("Invalid tags"), code="invalid")
            )

        return tags

    def save(self, commit=True):
        instance = super().save(commit=commit)

        instance.tags.clear()

        tags = self.cleaned_data.get("tags")

        for tag in tags:
            value = tag.get("value")

            if not value:
                continue

            tag, _ = Tag.objects.get_or_create(author=instance.author, name=value)

            instance.tags.add(tag)

        return instance


class TransactionFilterForm(forms.Form):
    def clean_tags(self):
        tags = self.cleaned_data.get("tags")

        if not tags:
            return []

        try:
            return json.loads(tags)
        except ValueError:
            self.add_error(
                "tags", ValidationError(message=_("Invalid tags"), code="invalid")
            )

        return tags

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
        queryset = Account.objects.active(owner=user).select_related("currency")

        self.fields["from_account"].queryset = queryset
        self.fields["to_account"].queryset = queryset

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
