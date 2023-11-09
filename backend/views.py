from backend.functions import read_yaml, import_data, encrypt_password, generate_token, is_admin, is_seller_or_admin
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import Category, Parameter, Store, User, Product, ProductStore, Order, OrderProduct, \
    ProductParameter
from backend.serializers import CategorySerializer, ParameterSerializer, StoreSerializer, UserViewSerializer, \
    UserCreateSerializer, ProductSerializer, ProductStoreSerializer, OrderSerializer, ProductParameterSerializer, \
    OrderProductSerializer, ViewStoreSerializer, ViewOrderSerializer, ViewProductStoreSerializer, ViewProductSerializer


# --------------------------------------------Категории-----------------------------------------
class CategoriesView(APIView):

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        result = is_admin(request)
        if result != 'ok':
            return result
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(f'Category {serializer.validated_data["name"]} created successfully',
                                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        result = is_admin(request)
        if result != 'ok':
            return result
        try:
            category = Category.objects.get(id=request.data['id'])
        except ObjectDoesNotExist:
            return Response(f'Category not found', status=status.HTTP_400_BAD_REQUEST)
        category.delete()
        return Response(f'Category deleted successfully', status=status.HTTP_200_OK)


    def patch(self, request):
        result = is_admin(request)
        if result != 'ok':
            return result
        serializer = CategorySerializer(data=request.data)
        try:
            category = Category.objects.get(id=request.data['id'])
        except ObjectDoesNotExist:
            return Response(f'Category {request.data["name"]} not found', status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.update(category, request.data)
            if serializer.errors == {}:
                return Response(f'Category updated successfully', status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------Параметры----------------------------------------
class ParametersView(APIView):
    def get(self, request):
        parameters = Parameter.objects.all()
        serializer = ParameterSerializer(parameters, many=True)
        return Response(serializer.data)

    def post(self, request):
        result = is_seller_or_admin(request)
        if result != 'ok':
            return result
        serializer = ParameterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(f'Parameter {serializer.validated_data["name"]} created successfully',
                                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        result = is_admin(request)
        if result != 'ok':
            return result
        parameter_id = request.data['id']
        try:
            parameter = Parameter.objects.get(id=parameter_id)
        except ObjectDoesNotExist:
            return Response('Parameter not found', status=status.HTTP_400_BAD_REQUEST)
        parameter.delete()
        return Response(f'Parameter deleted successfully', status=status.HTTP_200_OK)

    def patch(self, request):
        result = is_admin(request)
        if result != 'ok':
            return result
        serializer = ParameterSerializer(data=request.data)
        try:
            parameter = Parameter.objects.get(id=request.data['id'])
        except ObjectDoesNotExist:
            return Response(f'Parameter {request.data["name"]} not found', status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.update(parameter, request.data)
            if serializer.errors == {}:
                return Response(f'Parameter updated successfully', status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------------------------Магазины----------------------------------------
class StoresView(APIView):
    def get(self, request):
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True, )
        return Response(serializer.data)

    def post(self, request):
        result = is_admin(request)
        if result != 'ok':
            return result
        try:
            User.objects.get(id=request.data['owner'])
        except ObjectDoesNotExist:
            return Response(f'Please create user {request.data["owner"]} first', status=status.HTTP_400_BAD_REQUEST)
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(f'Store {serializer.validated_data["name"]} created successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        result = is_admin(request)
        if result != 'ok':
            return result
        try:
            user = User.objects.get(id=request.data['owner'])
        except ObjectDoesNotExist:
            return Response(f'Please create user first', status=status.HTTP_400_BAD_REQUEST)
        try:
            store = Store.objects.get(id=request.data['id'])
        except ObjectDoesNotExist:
            return Response(f'Store {request.data["name"]} not found', status=status.HTTP_400_BAD_REQUEST)
        mutable_request = request.data.copy()
        mutable_request['owner'] = user.id
        serializer = StoreSerializer(store, data=mutable_request)
        if serializer.is_valid():
            serializer.update(store, request.data)
            if serializer.errors == {}:
                return Response(f'Store updated successfully', status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        result = is_admin(request)
        if result != 'ok':
            return result
        try:
            store = Store.objects.get(id=request.data['id'])
        except ObjectDoesNotExist:
            return Response('Store not found', status=status.HTTP_400_BAD_REQUEST)
        store.delete()
        return Response(f'Store deleted successfully', status=status.HTTP_200_OK)


# ---------------------------------------------Пользователи-------------------------------------
class UsersView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserViewSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        result = is_admin(request)
        if result != 'ok':
            return result
        mutable_request = request.data.copy()
        mutable_request['password'] = encrypt_password(mutable_request['password'])
        mutable_request['token'] = generate_token()
        serializer = UserCreateSerializer(data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(f'User created successfully', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        result = is_admin(request)
        if result != 'ok':
            return result
        mutable_request = request.data.copy()
        mutable_request['password'] = encrypt_password(mutable_request['password'])
        mutable_request['token'] = generate_token()
        try:
            user = User.objects.get(id=mutable_request['owner'])
        except ObjectDoesNotExist:
            return Response('User not found', status=status.HTTP_400_BAD_REQUEST)
        serializer = UserCreateSerializer(user, data=mutable_request)
        if serializer.is_valid():
            serializer.update(user, mutable_request)
            if serializer.errors == {}:
                return Response(f'User updated successfully', status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        result = is_admin(request)
        if result != 'ok':
            return result
        try:
            user = User.objects.get(id=request.data['id'])
        except ObjectDoesNotExist:
            return Response('User not found', status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response(f'User deleted successfully', status=status.HTTP_200_OK)

# ----------------------------------------------Товары------------------------------------------
class ProductsView(APIView):

    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        serializer = ViewProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        result = is_seller_or_admin(request)
        if result != 'ok':
            return result
        category_id = request.data['category']
        try:
            Category.objects.get(id=category_id)
        except ObjectDoesNotExist:
            return Response('Category not found', status=status.HTTP_400_BAD_REQUEST)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(f'Product {serializer.validated_data["name"]} created successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        result = is_admin(request)
        if result != 'ok':
            return result
        category_id = request.data['category']
        try:
            Category.objects.get(id=category_id)
        except ObjectDoesNotExist:
            return Response('Category not found', status=status.HTTP_400_BAD_REQUEST)
        product_id = request.data['id']
        try:
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            return Response('Product not found', status=status.HTTP_400_BAD_REQUEST)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(f'Product updated successfully', status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        result = is_admin(request)
        if result != 'ok':
            return result
        product_id = request.data['id']
        try:
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            return Response('Product not found', status=status.HTTP_400_BAD_REQUEST)
        product.delete()
        return Response(f'Product deleted successfully', status=status.HTTP_200_OK)


# ----------------------------------------------Товары в магазине------------------------------
class ProductStoreView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = ProductStore.objects.all()
        serializer = ViewProductStoreSerializer(queryset, many=True)
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


# ---------------------------------------------------Заказы------------------------------------
class OrderView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Order.objects.all()
        serializer = ViewOrderSerializer(queryset, many=True)
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

                # Добавляю выбранный товар в общий заказ
                ordered_product = OrderProduct.objects.create(order=order, product=product, store=store,
                                                              quantity=quantity, price=price)
                ordered_product.save()
                return Response(f'Product {product.name} in store {store.name} was added to order {order.id}')


    # def delete_order(self, request, *args, **kwargs):
    #     try:
    #         order = Order.objects.get(id=request.data['id'])
    #     except ObjectDoesNotExist:
    #         return Response('Order not found', status=status.HTTP_400_BAD_REQUEST)
    #     if request.data['delete']:
    #         order.delete()
    #         return Response(f'Order was permanently deleted',
    #                         status=status.HTTP_201_CREATED)
    #     else:
    #         order.status = 'deleted'
    #         order.save(update_fields=['status'])
    #         return Response(f'Order was marked as deleted',
    #                         status=status.HTTP_201_CREATED)
    #

    # def partial_delete(self, request, *args, **kwargs):


class CartView(APIView):

    def get(self, request):
        user = request.GET.get('user')
        # status = request.GET.get('status')
        try:
            active_order = Order.objects.get(user=user, status='active')
        except ObjectDoesNotExist:
            return Response(f'No active orders for user {user}.', status=status.HTTP_400_BAD_REQUEST)
        serializer = ViewOrderSerializer(active_order)
        return Response(serializer.data)


class ImportData(APIView):
    def post(self, request):
        filename = request.FILES['filename']
        loaded_data = read_yaml(filename)
        # шифрую пароли, создаю токены
        for user in loaded_data['users']:
            for key, value in user.items():
                value['password'] = encrypt_password(value['password'])
                value['token'] = generate_token()

        dataset = {'users': UserCreateSerializer,
                   'categories': CategorySerializer,
                   'stores': StoreSerializer,
                   'products': ProductSerializer,
                   'parameters': ParameterSerializer,
                   'orders': OrderSerializer,
                   'product_parameters': ProductParameterSerializer,
                   'products_in_store': ProductStoreSerializer,
                   'products_in_order': OrderProductSerializer,
                   }
        for key, value in dataset.items():
            try:
                my_response = import_data(loaded_data[key], value)
            except KeyError:
                continue
            if my_response != 'ok':
                return my_response

        return Response(f'All data from {filename} uploaded successfully ', status=status.HTTP_201_CREATED)
