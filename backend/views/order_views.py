from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import Order, OrderProduct, User, Product, Store, ProductStore
from backend.serializers.order_serializers import OrderProductSerializer
from django.core.exceptions import ObjectDoesNotExist


# from backend.functions import encrypt_password

class OrderView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = OrderProduct.objects.all()
        serializer = OrderProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        match request.data['method']:
            case 'delete_order':
                result = self.delete_order(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'post':
                # Проверка на корректный ввод количества товаров
                quantity = int(request.data['quantity'])
                if quantity < 1:
                    return Response('Quantity must be at least 1', status=status.HTTP_400_BAD)

                # проверяю на наличие пользователя
                username = request.data['username']
                try:
                    user = User.objects.get(name=username)
                except ObjectDoesNotExist:
                    return Response(f'User {username} not exists', status=status.HTTP_400_BAD_REQUEST)

                # проверяю на наличие товара в базе
                product_value = request.data['product']
                try:
                    product = Product.objects.get(name=product_value)
                except ObjectDoesNotExist:
                    return Response('Please create product first', status=status.HTTP_400_BAD_REQUEST)

                # проверяю на наличие магазина в базе
                store_value = request.data['store']
                try:
                    store = Store.objects.get(name=store_value)
                except ObjectDoesNotExist:
                    return Response('Please create store first', status=status.HTTP_400_BAD_REQUEST)

                # Проверяю есть ли такой товар в магазине
                try:
                    product_in_store = ProductStore.objects.get(product=product, store=store)
                except ObjectDoesNotExist:
                    return Response(f'No product {product.name} in store {store.name}',
                                    status=status.HTTP_400_BAD_REQUEST)

                # Проверяю достаточно ли товара в магазине
                if quantity > product_in_store.quantity:
                    return Response(f'Not enough {product.name} in store {store.name}',
                                    status=status.HTTP_400_BAD_REQUEST)
                price = float(product_in_store.price)

                # Проверяю есть ли активный заказ от этого пользователя, если нет, создаю
                try:
                    order = Order.objects.get(user=user, status='active')
                except ObjectDoesNotExist:
                    order = Order.objects.create(user=user, status='active')
                    order.save()

                # Проверяю, есть ли в заказе такой товар от того же магазина, если нет, добавляю
                # если есть, то увеличиваю количество товаров в заказе и усредняю цену
                try:
                    product_in_order = OrderProduct.objects.get(order=order, product=product, store=store)

                except ObjectDoesNotExist:
                    product_in_order = OrderProduct.objects.create(product=product, order=order, store=store,
                                                                   quantity=0, price=0)
                    product_in_order.save()

                current_price = float(product_in_order.price)
                current_quantity = int(product_in_order.quantity)
                product_in_order.quantity = current_quantity + quantity
                product_in_order.price = ((current_price * current_quantity + price * quantity) /
                                          (current_quantity + quantity))
                product_in_order.save(update_fields=['quantity', 'price'])
                return Response(f'Product {product.name} in store {store.name} was added to order {order.id}',)

    #             считать общую стоимость заказа

    def delete_order(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(id=request.data['id'])
        except ObjectDoesNotExist:
            return Response('Order not found', status=status.HTTP_400_BAD_REQUEST)
        if request.data['delete']:
            order.delete()
            return Response(f'Order was permanently deleted',
                            status=status.HTTP_201_CREATED)
        else:
            order.status = 'deleted'
            order.save(update_fields=['status'])
            return Response(f'Order was marked as deleted',
                            status=status.HTTP_201_CREATED)



    # def partial_delete(self, request, *args, **kwargs):