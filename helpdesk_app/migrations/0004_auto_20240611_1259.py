# Generated by Django 3.0.2 on 2024-06-11 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk_app', '0003_auto_20220520_1010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='first name'),
        ),
    ]
