# Generated by Django 3.1.7 on 2021-03-23 05:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0015_auto_20210322_1253'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appuser',
            old_name='long',
            new_name='lang',
        ),
    ]
