# Generated by Django 4.2 on 2023-04-10 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenders', '0006_alter_activetender_tender_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='customer_contact',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
