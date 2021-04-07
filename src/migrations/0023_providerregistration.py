# Generated by Django 3.1.7 on 2021-04-02 11:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0022_auto_20210402_0923'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProviderRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_provider_name', models.CharField(default='', max_length=200)),
                ('country_code', models.IntegerField()),
                ('phone_number', models.BigIntegerField()),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(default='', max_length=400)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='src.appuser')),
            ],
        ),
    ]
