# Generated by Django 2.2.15 on 2020-09-22 13:47

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("users", "0003_auto_20200922_1646")]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        )
    ]
