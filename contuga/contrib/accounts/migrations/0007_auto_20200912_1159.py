# Generated by Django 2.2.15 on 2020-09-12 08:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("accounts", "0006_auto_20200911_2224")]

    operations = [
        migrations.RemoveField(model_name="account", name="currency"),
        migrations.RenameField(
            model_name="account", old_name="currency_foreign_key", new_name="currency"
        ),
    ]