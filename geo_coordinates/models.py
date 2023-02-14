from django.db import models


class Coordinate(models.Model):
    address = models.CharField('Адрес', max_length=200, unique=True)
    lng = models.FloatField('Долгота', null=True)
    lat = models.FloatField('Широта', null=True)
    datetime = models.DateTimeField('Дата запроса', auto_now=True)
