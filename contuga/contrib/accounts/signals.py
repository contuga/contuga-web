from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from contuga.contrib.transactions.models import Transaction


@receiver(post_save, sender=Transaction, dispatch_uid="update_account_balance_on_save")
@receiver(
    post_delete, sender=Transaction, dispatch_uid="update_account_balance_on_delete"
)
def update_account_balance(sender, instance, **kwargs):
    account = instance.account
    new_balance = account.calculate_balance()

    if account.balance != new_balance:
        account.balance = new_balance
        account.save(update_fields=["balance"])
