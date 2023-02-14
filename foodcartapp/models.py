from geopy import distance
from collections import Counter
from .coordinates import fetch_coordinates, check_coordinates
from geo_coordinates.models import Coordinate

from django.db import models
from django.conf import settings
from django.db.models import Sum, F
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator, MaxValueValidator


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )
    lng = models.FloatField('Долгота')
    lat = models.FloatField('Широта')

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects.filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class OrderQuerySet(models.QuerySet):
    def calculate_total_sum(self):
        return self.annotate(
            total_sum=Sum(
                (F('order_items__quantity') * F('order_items__product__price'))
            )
        )

    def get_availability_restaurants(self):
        products_in_orders = {}
        rest_by_order = {}
        for order in self:
            items = OrderItem.objects.select_related('product').\
                filter(order=order)
            products_in_orders[order] = [
                item.product for item in items
            ]
        restaurants_menu_items = RestaurantMenuItem.objects.\
            filter(availability=True).select_related("product", "restaurant")
        for order, products_in_order in products_in_orders.items():
            restaurants_by_products = restaurants_menu_items.\
                filter(product__in=products_in_order)

            restaurants_by_products = [
                restaurant.restaurant for restaurant in restaurants_by_products
            ]
            number_of_restaurants = dict(Counter(restaurants_by_products))
            restaurants = []
            for restaurant, count in number_of_restaurants.items():
                restaurant_coordinate = (restaurant.lat, restaurant.lng)

                coordinates, is_created = Coordinate.objects.get_or_create(
                    address=order.address,
                    defaults={
                        'lng': check_coordinates(order, restaurants)[0],
                        'lat': check_coordinates(order, restaurants)[1],
                    },
                )
                # try:
                #     order_coordinate = sorted(
                #         fetch_coordinates(
                #             settings.YANDEX_API_KEY, order.address
                #         ),
                #         reverse=True
                #     )
                # except TypeError:
                #     restaurants.append(
                #         'Ошибка определения координат'
                #     )
                #     continue
                # if
                delivery_distance = distance.distance(
                    restaurant_coordinate,
                    (coordinates.lng, coordinates.lat)
                ).km
                if delivery_distance > 100:
                    restaurants.append(
                        'Ошибка определения координат'
                    )
                elif count == len(products_in_order):
                    restaurants.append(
                        f'{restaurant.name}  {round(delivery_distance, 1)} км.'
                    )
            restaurants = sorted(restaurants, key=lambda i: i[-8:-6])
            rest_by_order[order] = restaurants
        for order in self:
            order.restaurant_can_cook = rest_by_order[order]
        return self


class Status(models.TextChoices):
    RAW = 'RA', _('Необработанный')
    HIRED = 'HR', _('Принят в работу')
    ASSEMBLY = 'AS', _('Сборка')
    DELIVERY = 'DL', _('Доставка')
    END = 'EN', _('Выполнен')


class Payment(models.TextChoices):
    CASH = 'CS', _('Наличностью')
    CARD = 'CD', _('Электронно')
    RAW = 'NO', _('Невыбрано')


class Order(models.Model):
    status = models.CharField(
        'Статус заказа',
        max_length=2,
        choices=Status.choices,
        default=Status.RAW,
        db_index=True
    )
    payment = models.CharField(
        'Оплата',
        max_length=2,
        choices=Payment.choices,
        default=Payment.RAW,
        db_index=True
    )
    firstname = models.CharField('Имя', max_length=255, db_index=True)
    lastname = models.CharField('Фамилия', max_length=255, blank=True)
    phonenumber = PhoneNumberField('Телефон', db_index=True)
    address = models.CharField('Адрес', max_length=255)
    comment = models.TextField('Коментарий', null=True, blank=True)
    restaurant = models.ManyToManyField(
        Restaurant,
        verbose_name='Ресторан для приготовления',
        related_name='orders',
        blank=True,
    )
    registrated_at = models.DateTimeField(
        'Дата оформления',
        auto_now_add=True,
        db_index=True
    )
    called_at = models.DateTimeField(
        'Дата звонка',
        db_index=True,
        null=True,
        blank=True
    )
    delivered_at = models.DateTimeField(
        'Дата доставки',
        db_index=True,
        null=True,
        blank=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ['-registrated_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.phonenumber}'


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=500,
        blank=True,
    )
    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class OrderItemQuerySet(models.QuerySet):
    def price_sum(self):
        return self.annotate(sum_price=(F('quantity') * F('product__price')))


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='продукт'
    )
    quantity = models.PositiveSmallIntegerField(
        'Колличество',
        default=1,
        db_index=True,
        validators=[MinValueValidator(0),
                    MaxValueValidator(100)]
    )
    price = models.DecimalField(
        'Стоймость',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0, 'Цена не может быть меньше 0')]
    )
    objects = OrderItemQuerySet.as_manager()

    class Meta:
        verbose_name = 'Пункт меню заказа'
        verbose_name_plural = 'Пункты меню заказов'

    def __str__(self):
        return f"{self.product.name} - {self.order.firstname}"


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"
