# Generated by Django 3.2.15 on 2023-02-07 19:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_auto_20230207_1855'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-registrated_at'], 'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
    ]
