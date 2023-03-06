from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem, Order, OrderItem

from django.db import models
from django.db.models import F
from django.contrib import admin
from django.conf import settings
from django.shortcuts import reverse
from django.utils.html import format_html
from django.forms import TextInput, Textarea
from django.http import HttpResponseRedirect
from django.templatetags.static import static
from django.utils.http import url_has_allowed_host_and_scheme


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


class OrderInline(admin.TabularInline):
    model = Order
    fields = ('payment', 'firstname', 'phonenumber')
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline, OrderInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly,
        #  so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html(
            '<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url
        )
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html(
            '<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/>'
            '</a>',
            edit_url=edit_url, src=obj.image.url
        )
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('get_product', 'get_order', 'quantity', 'total_price')
    fields = ('quantity', 'total_price')

    def get_product(self, obj):
        return obj.product.name

    def get_order(self, obj):
        return obj.order.firstname


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'status', 'payment', 'firstname', 'lastname', 'phonenumber', 'address',
    )
    list_display_links = ('firstname', 'lastname', 'address')
    list_editable = ('status', 'payment')
    list_filter = ('status', 'registrated_at', 'called_at', 'delivered_at')
    readonly_fields = ('registrated_at',)
    inlines = [
        OrderItemInline,
    ]

    fieldsets = (
        ('Покупатель', {
            'fields': (
                ('status', 'payment'), ('firstname', 'lastname'),
                ('phonenumber', 'address'), ('comment',),
                ('cooking_restaurant',)
            ),
        },),
        ('Время', {
             'fields': (
                 ('registrated_at',),
                 ('called_at',),
                 ('delivered_at',)
             )
         })
    )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 70})},
    }

    def get_restaurant(self, obj):
        orders = Order.objects.all().get_restaurants_availability()
        restaurants_name = [
            restaurant.name for restaurant in orders.get(id=obj.id).restaurant
        ]
        return restaurants_name

    def response_post_save_change(self, request, obj):
        res = super().response_post_save_change(request, obj)
        if url_has_allowed_host_and_scheme(
            request.META['SERVER_NAME'], settings.ALLOWED_HOSTS
        ):
            if "next" in request.GET:
                return HttpResponseRedirect(request.GET['next'])
            else:
                return res

