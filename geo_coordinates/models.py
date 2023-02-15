from django.db import models


class Coordinate(models.Model):
    address = models.CharField('Адрес', max_length=200, unique=True)
    lng = models.FloatField('Долгота')
    lat = models.FloatField('Широта')
    datetime = models.DateTimeField('Дата запроса', auto_now=True)
