# Generated by Django 4.2 on 2023-04-09 06:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenders', '0003_activetender'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=500, unique=True)),
                ('customer_edrpou', models.CharField(max_length=100, unique=True)),
                ('customer_contact', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='DKNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=2000)),
            ],
        ),
        migrations.RemoveField(
            model_name='activetender',
            name='customer_contact',
        ),
        migrations.RemoveField(
            model_name='archivetender',
            name='customer_contact',
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=15)),
                ('dk_numbers', models.ManyToManyField(to='tenders.dknumber')),
            ],
        ),
        migrations.AlterField(
            model_name='activetender',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenders.customer'),
        ),
        migrations.AlterField(
            model_name='archivetender',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenders.customer'),
        ),
    ]
