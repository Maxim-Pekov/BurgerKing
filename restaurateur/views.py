from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from foodcartapp.geocoding import fetch_distance_by_coordinate
from foodcartapp.geocoding import save_coordinate_by_order_address
from foodcartapp.models import Order, Product, Restaurant, RestaurantMenuItem
from foodcartapp.models import OrderItem


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя',
        }),
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
        }),
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form,
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
        availability = {
            item.restaurant_id: item.availability
            for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False) for restaurant
            in restaurants
        ]

        products_with_restaurant_availability.append(
            (product, ordered_availability),
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability':
            products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.calculate_total_sum().fetch_lat_coordinate().\
        fetch_lng_coordinate(). \
        exclude(status=Order.Status.CLOSED). \
        prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product'),
            ),
        )

    context = []

    restaurants = Restaurant.objects.prefetch_related(
        Prefetch(
            'menu_items',
            queryset=RestaurantMenuItem.objects.
            filter(availability=True).
            select_related('product'),
        ),
    )

    restaurant_products_available = {}
    for restaurant in restaurants:
        restaurant_products_available[restaurant] = []
        for item in restaurant.menu_items.all():
            if item.availability:
                restaurant_products_available[restaurant].append(
                    item.product)

    restaurant_can_cook_by_order = {}
    for order in orders:
        restaurants = []
        order_item_ids = [product.product for product in
                          order.items.all()]
        order_coordinates = order.address_lat_coordinate, \
            order.address_lng_coordinate
        if None in order_coordinates:
            order_coordinates = save_coordinate_by_order_address(order)
        for restaurant in restaurant_products_available:
            restaurant_coordinate = (restaurant.lng, restaurant.lat)

            if all(item in restaurant_products_available[restaurant] for item
                   in order_item_ids):
                distace = fetch_distance_by_coordinate(
                    restaurant_coordinate, order_coordinates,
                )
                if not distace:
                    continue
                restaurants.append((restaurant.name, distace))
                restaurants = sorted(restaurants, key=lambda x: x[1])
        restaurant_can_cook_by_order[order] = restaurants
        context.append((order, restaurant_can_cook_by_order[order]))

    return render(request, template_name='order_items.html', context={
        'order_items': context,
    })
