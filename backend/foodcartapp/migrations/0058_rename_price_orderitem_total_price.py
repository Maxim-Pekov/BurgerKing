# Generated by Django 3.2.15 on 2023-03-01 18:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0057_alter_order_restaurant'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='price',
            new_name='total_price',
        ),
    ]