import requests

from geopy import distance
from django.conf import settings
from backend.geo_coordinates.models import Address


def fetch_coordinates(address, apikey=settings.YANDEX_API_KEY):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.\
        json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return (None, None)

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def fetch_distance_by_coordinate(restaurant_coordinate, order_coordinates):
    if None in order_coordinates:
        return
    delivery_distance = distance.distance(
        restaurant_coordinate,
        order_coordinates
    ).km
    return round(delivery_distance, 2)


def save_coordinate_by_order_address(order):
    address, is_created = Address.objects.get_or_create(
        address=order.address,
    )
    if is_created:
        address.lat, address.lng = fetch_coordinates(address.address)
        address.save()
        return address.lat, address.lng
