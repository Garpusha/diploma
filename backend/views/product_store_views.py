# Нужна проверка авторизации, добавлять/удалять/менять товар может только продавец

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import ProductStore, Product, Store
from backend.serializers.product_store_serializers import ProductStoreSerializer
from django.core.exceptions import ObjectDoesNotExist


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
                # создаю нулевую запись, иначе прибавляю количество к уже имеющимся
                try:
                    products_in_store = ProductStore.objects.get(product=product, store=store)
                    in_stock = products_in_store.quantity
                    current_price = float(products_in_store.price)
                except ObjectDoesNotExist:
                    products_in_store = ProductStore.objects.create(product=product, store=store,
                                                                    quantity=0, price=0)
                    products_in_store.save()
                    in_stock = 0
                    current_price = 0

                products_in_store.quantity = quantity_value + in_stock

                # Цена на складе усредняется с новой поставкой для упрощения
                products_in_store.price = ((price_value * quantity_value + current_price * in_stock) /
                                           (quantity_value + in_stock))
                products_in_store.save(update_fields=['quantity', 'price'])
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)
        return Response(f'Product {product.name} added to store {store.name} successfully',
                        status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        product_name = request.data.get('product', None)
        try:
            product = Product.objects.get(name=product_name)
        except ObjectDoesNotExist:
            return Response('Product not found', status=status.HTTP_400_BAD_REQUEST)
        store_name = request.data.get('store', None)
        try:
            store = Store.objects.get(name=store_name)
        except ObjectDoesNotExist:
            return Response('Store not found', status=status.HTTP_400_BAD_REQUEST)
        try:
            product_in_store = ProductStore.objects.get(product=product, store=store)
        except ObjectDoesNotExist:
            return Response(f'No product {product.name} in store {store.name}',
                            status=status.HTTP_400_BAD_REQUEST)
        product_in_store.delete()
        return Response(f'Product {product.name} deleted from {store.name} successfully',
                        status=status.HTTP_201_CREATED)


    # def partial_delete(self, request, *args, **kwargs):