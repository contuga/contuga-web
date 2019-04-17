from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q

from . import constants
from contuga.models import TimestampModel

UserModel = get_user_model()


class Account(TimestampModel):
    name = models.CharField(_('Name'),
                            max_length=254)
    currency = models.CharField(_('Currency'),
                                max_length=3,
                                choices=constants.CURRENCY_CHOICES)
    owner = models.ForeignKey(UserModel,
                              related_name='accounts',
                              on_delete=models.CASCADE)
    description = models.CharField(_('Description'),
                                   max_length=1000,
                                   blank=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')

    def __str__(self):
        return f'{self.name} - {self.owner}'

    def get_absolute_url(self):
        return reverse('accounts:detail', kwargs={'pk': self.pk})

    @property
    def is_balance_positive(self):
        return self.balance > 0

    @property
    def is_balance_negative(self):
        return self.balance < 0

    @cached_property
    def balance(self):
        expenditures, incomes = self.transactions.aggregate(
            expenditures=Sum('amount', filter=Q(type='expenditure')),
            incomes=Sum('amount', filter=Q(type='income'))
        ).values()

        incomes = incomes or 0
        expenditures = expenditures or 0
        return incomes - expenditures
