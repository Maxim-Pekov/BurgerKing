from django.contrib import admin
from .models import Coordinate


@admin.register(Coordinate)
class CoordinateAdmin(admin.ModelAdmin):
    list_display = [
        'address',
        'lng',
        'lat',
        'datetime'
    ]
