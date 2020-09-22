# Generated by Django 2.2.15 on 2020-09-22 10:47
import uuid

from django.db import migrations


def forward(apps, schema_editor):
    Account = apps.get_model("accounts", "Account")

    for account in Account.objects.all():
        account.uuid = uuid.uuid4()
        account.save()


class Migration(migrations.Migration):

    dependencies = [("accounts", "0012_account_uuid")]

    operations = [migrations.RunPython(forward, migrations.RunPython.noop)]
