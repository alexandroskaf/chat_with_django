# Generated by Django 3.0.2 on 2021-08-27 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='first name'),
        ),
    ]
