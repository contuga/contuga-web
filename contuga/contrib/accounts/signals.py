from django.db.models import OuterRef, Q, Subquery, Sum
from django.db.models.functions import Coalesce
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from contuga.contrib.transactions.models import Transaction

from .models import Account


@receiver(post_save, sender=Transaction, dispatch_uid="update_account_balance_on_save")
@receiver(
    post_delete, sender=Transaction, dispatch_uid="update_account_balance_on_delete"
)
def update_account_balance(sender, instance, **kwargs):
    transactions = (
        Transaction.objects.filter(account__pk=OuterRef("pk"))
        .order_by()
        .values("account")
    )
    balance = transactions.annotate(
        balance=Coalesce(Sum("amount", filter=Q(type="income")), 0)
        - Coalesce(Sum("amount", filter=Q(type="expenditure")), 0)
    ).values("balance")

    # If there are no transactions, the subquery will not return a balance and
    # Coalesce prevents failing due to NOT NULL constraint.
    Account.objects.filter(owner=instance.author).update(
        balance=Coalesce(Subquery(balance), 0)
    )
