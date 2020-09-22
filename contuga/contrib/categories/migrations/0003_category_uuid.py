# Generated by Django 2.2.15 on 2020-09-22 12:27

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("categories", "0002_category_transaction_type")]

    operations = [
        migrations.AddField(
            model_name="category",
            name="uuid",
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True),
        )
    ]
