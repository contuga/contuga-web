# Generated by Django 3.1.4 on 2021-02-27 11:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tags", "0001_initial"),
        ("transactions", "0003_transaction_expenditure_counterpart"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="tags",
            field=models.ManyToManyField(
                related_name="transactions", to="tags.Tag", verbose_name="Tags"
            ),
        )
    ]
