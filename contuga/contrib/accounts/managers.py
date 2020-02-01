from django.db import models


class AccountManager(models.Manager):
    def active(self, **kwargs):
        return self.filter(is_active=True, **kwargs)

    def deactivated(self, **kwargs):
        return self.filter(is_active=False, **kwargs)
