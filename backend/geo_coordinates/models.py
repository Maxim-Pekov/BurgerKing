from django.db import models


class Address(models.Model):
    address = models.CharField('Адрес', max_length=200, unique=True)
    lng = models.FloatField('Долгота', null=True)
    lat = models.FloatField('Широта', null=True)
    created_at = models.DateTimeField('Дата запроса', auto_now=True)
