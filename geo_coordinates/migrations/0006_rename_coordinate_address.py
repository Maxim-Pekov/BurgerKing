# Generated by Django 3.2.15 on 2023-03-06 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo_coordinates', '0005_auto_20230301_0722'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Coordinate',
            new_name='Address',
        ),
    ]