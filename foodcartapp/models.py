from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.db.models import OuterRef, Subquery
from django.utils.translation import gettext_lazy as _

from geo_coordinates.models import Address

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
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
        max_length=50,
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
                F('items__total_price'),
            ),
        )

    def fetch_lat_coordinate(self):
        address = Address.objects.filter(address=OuterRef('address'))
        return self.annotate(
            address_lat_coordinate=Subquery(address.values("lat")),
        )

    def fetch_lng_coordinate(self):
        address = Address.objects.filter(address=OuterRef('address'))
        return self.annotate(address_lng_coordinate=Subquery(address.values(
            "lng")))


class Order(models.Model):
    class Status(models.TextChoices):
        RECEIVED = 'RE', _('Необработанный')
        IN_PROCESSING = 'PR', _('Принят в работу')
        COOKING = 'CO', _('Приготовление')
        DELIVERY = 'DL', _('Доставка')
        CLOSED = 'CL', _('Выполнен')

    class Payment(models.TextChoices):
        CASH = 'CS', _('Наличностью')
        CARD = 'CD', _('Электронно')
        RAW = 'NO', _('Не выбрано')

    status = models.CharField(
        'Статус заказа',
        max_length=2,
        choices=Status.choices,
        default=Status.RECEIVED,
        db_index=True,
    )
    payment = models.CharField(
        'Оплата',
        max_length=2,
        choices=Payment.choices,
        default=Payment.RAW,
        db_index=True,
    )
    firstname = models.CharField('Имя', max_length=255, db_index=True)
    lastname = models.CharField('Фамилия', max_length=255, blank=True)
    phonenumber = PhoneNumberField('Телефон', db_index=True)
    address = models.CharField('Адрес', max_length=255)
    comment = models.TextField('Коментарий', blank=True)
    cooking_restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='Ресторан для приготовления',
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    registered_at = models.DateTimeField(
        'Дата оформления',
        auto_now_add=True,
        db_index=True,
    )
    called_at = models.DateTimeField(
        'Дата звонка',
        db_index=True,
        null=True,
        blank=True,
    )
    delivered_at = models.DateTimeField(
        'Дата доставки',
        db_index=True,
        null=True,
        blank=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ['-registered_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.phonenumber}'


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
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
        validators=[MinValueValidator(0)],
    )
    image = models.ImageField(
        'картинка',
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


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='продукт',
    )
    quantity = models.PositiveSmallIntegerField(
        'Колличество',
        db_index=True,
        validators=[MinValueValidator(1),
                    MaxValueValidator(100)],
    )
    total_price = models.DecimalField(
        'Стоимость',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0, 'Цена не может быть меньше 0')],
    )

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
        db_index=True,
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product'],
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"
