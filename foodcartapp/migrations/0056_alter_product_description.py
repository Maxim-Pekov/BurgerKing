# Generated by Django 3.2.15 on 2023-02-13 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0055_remove_product_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, max_length=500, verbose_name='описание'),
        ),
    ]
