import json

from django.http import JsonResponse
from django.templatetags.static import static
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Product, Order
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_info = request.data
    print(order_info)
    api_order_keys = {'products': list, 'firstname': str, 'lastname': str, \
        'phonenumber': str, 'address': str}

    for key, value in api_order_keys.items():
        try:
            order_info_value = order_info[key]
            if not isinstance(order_info_value, value):
                content = {
                    'Error. Format is incorrect. : '
                    f'Parameter "{key}": "{order_info_value}", '
                    f'format is incorrect or not '
                    f'presented, expected "{value}" format'
                }
                return Response(content,
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except KeyError:
            content = {
                'Error. Required parameter missing : '
                f'Required parameter "{key}" is missing'
            }
            return Response(
                content, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        if order_info_value in ([], ''):
            content = {
                'Error. Value is incorrect : '
                f'Value "{key}" of parameter "{order_info_value}" is '
                f'not supported'
            }
            return Response(content,
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if key == 'phonenumber' and order_info_value[2:5] == '000':
            content = {
                'Error. Phonenumber is incorrect : '
                f'Value "{key}" of parameter "{order_info_value}" is '
                f'not supported'
            }
            return Response(content,
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # if key == 'products' and order_info_value[]:
        #
        #     content = {
        #         'Error. Phonenumber is incorrect : '
        #         f'Value "{key}" of parameter "{order_info_value}" is '
        #         f'not supported'
        #     }
        #     return Response(content,
        #                     status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    order = Order.objects.create(
        name=order_info['firstname'],
        surname=order_info['lastname'],
        phone=order_info['phonenumber'],
        address=order_info['address']
    )

    product_count = Product.objects.all().count()

    for product_by_order in order_info['products']:
        product_id = product_by_order['product']
        product_qlt = product_by_order['quantity']

        if product_id > product_count:
            content = {
                'Error. Id of product is incorrect : '
                f'Value "{product_id}" of parameter "product[id]" is '
                f'not supported'
            }
            return Response(content,
                            status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        product = Product.objects.get(id=product_id)
        product.order = order
        product.quantity = product_qlt
        product.save()
    return JsonResponse({})
