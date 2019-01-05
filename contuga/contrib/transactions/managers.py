from django.db import models

from . import constants


class TransactionManager(models.Manager):
    def income(self):
        return self.filter(kind=constants.INCOME)

    def expenditures(self):
        return self.filter(kind=constants.EXPENDITURE)
