# Generated by Django 5.1.1 on 2024-10-08 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutri_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
