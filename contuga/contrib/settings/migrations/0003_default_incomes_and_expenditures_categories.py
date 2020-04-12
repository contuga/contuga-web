# Generated by Django 2.2.11 on 2020-04-07 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0002_category_transaction_type"),
        ("settings", "0002_create_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="settings",
            name="default_expenditures_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="default_usages_for_expenditures",
                to="categories.Category",
                verbose_name="Default category for expenditures",
            ),
        ),
        migrations.AddField(
            model_name="settings",
            name="default_incomes_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="default_usages_for_incomes",
                to="categories.Category",
                verbose_name="Default category for incomes",
            ),
        ),
    ]