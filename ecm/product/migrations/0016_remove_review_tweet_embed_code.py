# Generated by Django 5.0.2 on 2025-05-16 10:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0015_review'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='tweet_embed_code',
        ),
    ]
