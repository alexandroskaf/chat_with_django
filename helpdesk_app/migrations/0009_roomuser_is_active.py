# Generated by Django 3.2.25 on 2024-11-05 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk_app', '0008_roomuser_last_seen_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomuser',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
