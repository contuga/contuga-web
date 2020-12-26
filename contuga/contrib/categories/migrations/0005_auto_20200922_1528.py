# Generated by Django 2.2.15 on 2020-09-22 12:28

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("categories", "0004_fill_uuid")]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        )
    ]