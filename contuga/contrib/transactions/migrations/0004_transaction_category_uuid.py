# Generated by Django 2.2.15 on 2020-09-22 12:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0005_auto_20200922_1528"),
        ("transactions", "0003_auto_20190406_1907"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="category_uuid",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="transactions_uuid",
                to="categories.Category",
                to_field="uuid",
                verbose_name="Category",
            ),
        )
    ]