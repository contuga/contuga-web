# Generated by Django 2.2.15 on 2020-09-22 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("settings", "0011_auto_20200922_1621")]

    operations = [
        migrations.RemoveField(model_name="settings", name="default_account"),
        migrations.RenameField(
            model_name="settings",
            old_name="default_account_uuid",
            new_name="default_account",
        ),
    ]
