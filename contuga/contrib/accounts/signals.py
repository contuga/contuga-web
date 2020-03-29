from django.db.models.signals import post_save
from django.dispatch import receiver

from contuga.contrib.transactions.models import Transaction


@receiver(post_save, sender=Transaction, dispatch_uid="update_account_balance")
def update_account_balance(sender, instance, created, **kwargs):
    account = instance.account
    new_balance = account.calculate_balance()

    if account.balance != new_balance:
        account.balance = new_balance
        account.save(update_fields=["balance"])
