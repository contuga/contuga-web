# Generated by Django 2.2.15 on 2020-09-22 13:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0011_auto_20200922_1615"),
        ("accounts", "0015_auto_20200922_1615"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="account",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transactions",
                to="accounts.Account",
                verbose_name="Account",
            ),
        )
    ]
