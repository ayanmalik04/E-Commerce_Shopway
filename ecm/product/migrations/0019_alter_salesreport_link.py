# Generated by Django 5.0.2 on 2025-05-27 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0018_alter_salesreport_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesreport',
            name='link',
            field=models.URLField(default='http://127.0.0.1:8000/sales/', max_length=300),
        ),
    ]
