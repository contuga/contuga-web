from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from . import constants
from .models import Category


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        extra_kwargs = {"author": {"read_only": True}}

    def validate_transaction_type(self, transaction_type):
        if not self.instance or transaction_type == constants.ALL:
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

                raise serializers.ValidationError(message)
            return transaction_type
