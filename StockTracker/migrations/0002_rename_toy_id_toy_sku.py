# Generated by Django 4.1 on 2023-11-28 06:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StockTracker', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='toy',
            old_name='toy_id',
            new_name='sku',
        ),
    ]