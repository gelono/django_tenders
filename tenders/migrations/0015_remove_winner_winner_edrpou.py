# Generated by Django 4.2 on 2023-04-16 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenders', '0014_transactionout_transactionin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='winner',
            name='winner_edrpou',
        ),
    ]