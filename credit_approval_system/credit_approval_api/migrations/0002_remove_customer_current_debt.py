# Generated by Django 5.0.1 on 2024-02-02 17:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('credit_approval_api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='current_debt',
        ),
    ]