# Generated by Django 3.1.7 on 2021-03-23 08:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0017_usernotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernotification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usernotification',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
