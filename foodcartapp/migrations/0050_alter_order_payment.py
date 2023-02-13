# Generated by Django 3.2.15 on 2023-02-07 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_order_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('CS', 'Наличностью'), ('CD', 'Электронно'), ('NO', 'Невыбрано')], db_index=True, default='NO', max_length=2, verbose_name='Оплата'),
        ),
    ]