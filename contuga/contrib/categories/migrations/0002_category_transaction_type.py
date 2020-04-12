# Generated by Django 2.2.11 on 2020-04-06 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("categories", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="category",
            name="transaction_type",
            field=models.CharField(
                choices=[
                    ("income", "Income"),
                    ("expenditure", "Expenditure"),
                    ("all", "All"),
                ],
                default="all",
                help_text="Select which transaction type this category will be used for.",
                max_length=254,
                verbose_name="Transaction type",
            ),
        )
    ]
