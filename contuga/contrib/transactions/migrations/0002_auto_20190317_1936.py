# Generated by Django 2.1.7 on 2019-03-17 19:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='kind',
            new_name='type',
        ),
    ]
