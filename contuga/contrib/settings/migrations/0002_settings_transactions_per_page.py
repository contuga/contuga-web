# Generated by Django 3.1.4 on 2021-01-30 10:53

import django.core.validators
from django.db import migrations, models

from .. import constants


class Migration(migrations.Migration):
    dependencies = [("settings", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="settings",
            name="transactions_per_page",
            field=models.IntegerField(
                default=constants.DEFAULT_TRANSACTIONS_PER_PAGE,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Transactions per page",
            ),
        )
    ]
