from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


from . import constants
from .models import Category


class CategoryUpdateForm(forms.ModelForm):
    def clean_transaction_type(self):
        transaction_type = self.cleaned_data.get("transaction_type")

        if transaction_type == constants.ALL:
            return transaction_type
        else:
            other_usages = self.instance.transactions.exclude(type=transaction_type)

            if other_usages:
                if transaction_type == constants.EXPENDITURE:
                    other_type = _("Income")
                else:
                    other_type = _("Expenditure")
                message = _(
                    f"This category is still used for transactions of type {other_type}. "
                    "Please, fix all transactions before changing the category type."
                )

                self.add_error(
                    "transaction_type", ValidationError(message=message, code="invalid")
                )
            return transaction_type

    class Meta:
        model = Category
        fields = ("name", "transaction_type", "description")
