# Generated by Django 3.1.7 on 2021-04-02 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0023_providerregistration'),
    ]

    operations = [
        migrations.AddField(
            model_name='providerregistration',
            name='image',
            field=models.ImageField(default=1, upload_to='media'),
            preserve_default=False,
        ),
    ]
