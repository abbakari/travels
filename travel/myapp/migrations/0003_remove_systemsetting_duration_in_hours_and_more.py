# Generated by Django 5.2.1 on 2025-05-29 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_systemsetting'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='systemsetting',
            name='duration_in_hours',
        ),
        migrations.AddField(
            model_name='systemsetting',
            name='duration_in_minutes',
            field=models.IntegerField(default=1),
        ),
    ]
