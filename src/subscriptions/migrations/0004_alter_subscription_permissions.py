# Generated by Django 5.2 on 2025-04-12 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('subscriptions', '0003_alter_subscription_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='permissions',
            field=models.ManyToManyField(to='auth.permission'),
        ),
    ]
