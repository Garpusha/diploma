# Нужна проверка авторизации, добавлять/удалять/менять товар может только продавец

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import ProductStore, Product, Store
from backend.serializers.product_store_serializers import ProductStoreSerializer
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
# from backend.functions import encrypt_password

class ProductStoreView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = ProductStore.objects.all()
        serializer = ProductStoreSerializer(queryset, many=True)
        return Response(serializer.data)


    def post(self, request, *args, **kwargs):
        match request.data['method']:
            case 'delete':
                result = self.delete(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'post':
                # mutable_request = request.data.copy()

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

                quantity_value = int(request.data['quantity'])
                price_value = float(request.data['price'])

                # Считываю количество товаров в магазине, если таких товаров в этом магазине нет,
                # создаю нулевую запись
                try:
                    products_in_store = ProductStore.objects.get(product=product, store=store)
                    in_stock = products_in_store.quantity
                except ObjectDoesNotExist:
                    products_in_store = ProductStore.objects.create(product=product, store=store,
                                                                    quantity=0, price=0)
                    products_in_store.save()
                    in_stock = 0

                products_in_store.quantity = quantity_value + in_stock
                products_in_store.price = price_value
                products_in_store.save(update_fields=['quantity', 'price'])
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)
        return Response(f'Product {product.name} added to store {store.name} successfully',
                        status=status.HTTP_201_CREATED)
    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('id', None)
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response(f'Product deleted successfully',
                        status=status.HTTP_201_CREATED)
