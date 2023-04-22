# Generated by Django 4.2 on 2023-04-09 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArchiveTenders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(max_length=500)),
                ('status', models.CharField(max_length=100)),
                ('tender_name', models.CharField(max_length=1000)),
                ('dk_numbers', models.CharField(max_length=1000)),
                ('customer', models.CharField(max_length=500)),
                ('initial_price', models.FloatField(null=True)),
                ('finish_price', models.FloatField(null=True)),
                ('winner', models.CharField(max_length=500)),
                ('publication_date', models.DateField()),
                ('customer_contact', models.CharField(max_length=200)),
                ('inner_status', models.CharField(default='old', max_length=20)),
            ],
        ),
    ]