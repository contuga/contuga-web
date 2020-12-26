# Generated by Django 2.2.15 on 2020-09-22 12:37

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0005_auto_20200922_1528"),
        # Removing id foreign keys before removing the field
        ("settings", "0008_auto_20200922_1538"),
        ("transactions", "0006_auto_20200922_1543"),
    ]

    operations = [
        migrations.RemoveField(model_name="category", name="id"),
        migrations.AlterField(
            model_name="category",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, primary_key=True, serialize=False
            ),
        ),
    ]