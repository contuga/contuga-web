# Generated by Django 2.2.15 on 2020-09-22 13:12

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("accounts", "0013_fill_uuid")]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        )
    ]
