# Generated by Django 5.0.2 on 2025-05-08 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_alter_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='productt',
            name='category',
            field=models.CharField(choices=[('Watches', 'Watches'), ('Shoes', 'Shoes'), ('Electronics', 'Electronics'), ('Clothing', 'Clothing'), ('Groceries', 'Groceries')], default=False, max_length=50),
        ),
    ]
