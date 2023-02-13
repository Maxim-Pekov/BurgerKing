import requests

from collections import Counter
from pprint import pprint
from geopy import distance
from environs import Env

from django import forms
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order, Status, OrderItem, \
    Restaurant, RestaurantMenuItem


env = Env()
env.read_env()

apikey = env('YANDEX_API_KEY')


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.calculate_total_sum().exclude(
        status=Status.END).get_availability_restaurants()
    # products_in_orders = {}
    # rest_by_order = {}
    # for order in orders:
    #     items = OrderItem.objects.select_related('product').filter(
    #             order=order)
    #     products_in_orders[order] = [
    #         item.product for item in items
    #     ]
    # restaurants_menu_items = RestaurantMenuItem.objects.filter(availability=True).select_related("product", "restaurant")
    # for order, products_in_order in products_in_orders.items():
    #     r = restaurants_menu_items.filter(product__in=products_in_order)
    #     f = [i.restaurant for i in r]
    #     z = dict(Counter(f))
    #     rest = []
    #     for key, value in z.items():
    #         if value == len(products_in_order):
    #             rest.append(key)
    #     pprint(r)
    #     rest_by_order[order] = rest

    # pul = fetch_coordinates(apikey, 'Богатырский 48')
    # b = fetch_coordinates(apikey, '<Богатырский 52')
    # print(pul)
    # print(sorted(pul, reverse=True))

    wellington = (-41.32, 174.81)
    salamanca = (40.96, -5.50)

    print(distance.distance(wellington, salamanca).km)
    context = []
    for order in orders:
        try:
            context.append(
                (order, ('restaurant_selected', order.restaurant.all()[0].name))
            )
        except IndexError:
            context.append(
                (order, ('restaurant_not_selected', order.restaurant_can_cook))
            )
    return render(request, template_name='order_items.html', context={
        'order_items': context,
    })
