from import_export import resources

from .models import Transaction


class TransactionResource(resources.ModelResource):
    class Meta:
        model = Transaction
        fields = ("type", "amount", "category", "account", "description")

    def dehydrate_category(self, transaction):
        return transaction.category.name if transaction.category else ""

    def dehydrate_account(self, transaction):
        return transaction.account.name
