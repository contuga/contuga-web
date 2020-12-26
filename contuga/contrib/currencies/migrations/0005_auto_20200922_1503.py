# Generated by Django 2.2.15 on 2020-09-22 12:03

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("currencies", "0004_auto_20200922_1502"),
        # Removing id foreign keys before removing the field
        ("accounts", "0010_auto_20200922_1414"),
    ]

    operations = [
        migrations.RemoveField(model_name="currency", name="id"),
        migrations.AlterField(
            model_name="currency",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, primary_key=True, serialize=False
            ),
        ),
    ]