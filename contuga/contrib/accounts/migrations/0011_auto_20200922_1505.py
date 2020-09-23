# Generated by Django 2.2.15 on 2020-09-22 12:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0010_auto_20200922_1414"),
        ("currencies", "0005_auto_20200922_1503"),
    ]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="currency",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="accounts",
                to="currencies.Currency",
            ),
        )
    ]