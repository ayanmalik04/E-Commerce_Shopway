# Generated by Django 5.0.2 on 2025-03-08 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_contactmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='regemail',
            field=models.EmailField(default=False, max_length=254),
        ),
    ]
