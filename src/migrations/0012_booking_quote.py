# Generated by Django 3.1.7 on 2021-03-22 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0011_appuser_device_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='quote',
            field=models.CharField(default='', max_length=2560),
        ),
    ]
