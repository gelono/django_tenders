# Generated by Django 4.2 on 2023-04-18 08:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenders', '0016_remove_activetender_winner_old_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscriber',
            old_name='subscriber',
            new_name='user',
        ),
    ]
