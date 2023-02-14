import requests
from geopy import distance
from django.conf import settings


def fetch_coordinates(apikey, address):
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
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def check_coordinates(order, restaurants):
    # restaurant_coordinate = (restaurant.lat, restaurant.lng)
    try:
        order_coordinate = sorted(
            fetch_coordinates(
                settings.YANDEX_API_KEY, order.address
            ),
            reverse=True
        )
    except TypeError:
        restaurants.append(
            'Ошибка определения координат'
        )
        return 'error'
    # delivery_distance = distance.distance(
    #     restaurant_coordinate,
    #     order_coordinate
    # ).km
    # if delivery_distance > 100:
    #     restaurants.append(
    #         'Ошибка определения координат'
    #     )
    #     return 'error'
    # elif count == len(products_in_order):
    #     restaurants.append(
    #         f'{restaurant.name}  {round(delivery_distance, 1)} км.'
    #     )
    return order_coordinate
