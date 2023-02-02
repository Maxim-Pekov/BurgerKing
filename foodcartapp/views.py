from django.http import JsonResponse
from django.templatetags.static import static
from .models import Product, Order, OrderItem
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer


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


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']


@api_view(['POST'])
def register_order(request):
    order_info = request.data

    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)  # выкинет
    # ValidationError

    order = Order.objects.create(
        firstname=order_info['firstname'],
        lastname=order_info['lastname'],
        phonenumber=order_info['phonenumber'],
        address=order_info['address']
    )

    for product_by_order in order_info['products']:
        product_id = product_by_order['product']
        product_qlt = product_by_order['quantity']

        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=product_qlt
        )
    return Response({
        'good': 'good',
    })
