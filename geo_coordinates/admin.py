from django.contrib import admin
from .models import Address


@admin.register(Address)
class CoordinateAdmin(admin.ModelAdmin):
    list_display = [
        'address',
        'lng',
        'lat',
        'created_at'
    ]
