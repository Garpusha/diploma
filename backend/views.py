from django.db.models import Q

from backend.functions import read_yaml, import_data, encrypt_password, generate_token, \
    is_exists, is_token_exists, is_role, is_store_owner, get_id_by_name
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets
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
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(f'Category {serializer.validated_data["name"]} created successfully',
                                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

        category_id = request.data['id']
        result = is_exists(category_id, Category)
        if result:
            result.delete()
            return Response(f'Category deleted successfully', status=status.HTTP_200_OK)
        return Response(f'Category not found', status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

        serializer = CategorySerializer(data=request.data)
        category_id = request.data['id']
        result = is_exists(category_id, Category)
        if not result:
            return Response(f'Category not found', status=status.HTTP_404_NOT_FOUND)
        if serializer.is_valid():
            serializer.update(result, request.data)
            if serializer.errors == {}:
                return Response(f'Category updated successfully', status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------Параметры----------------------------------------
class ParametersView(APIView):
    def get(self, request):
        queryset = Parameter.objects.all()
        serializer = ParameterSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin', 'seller']):
            return Response('Admin or seller rights required', status=status.HTTP_400_BAD_REQUEST)

        serializer = ParameterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(f'Parameter {serializer.validated_data["name"]} created successfully',
                                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

        parameter_id = request.data['id']
        result = is_exists(parameter_id, Parameter)
        if result:
            result.delete()
            return Response(f'Parameter deleted successfully', status=status.HTTP_200_OK)
        return Response(f'Parameter not found', status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

        serializer = ParameterSerializer(data=request.data)
        parameter_id = request.data['id']
        result = is_exists(parameter_id, Parameter)
        if not result:
            return Response(f'Parameter not found', status=status.HTTP_404_NOT_FOUND)
        if serializer.is_valid():
            serializer.update(result, request.data)
            if serializer.errors == {}:
                return Response(f'Parameter updated successfully', status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------------------------Магазины----------------------------------------
class StoresView(APIView):
    def get(self, request):
        queryset = Store.objects.all()
        serializer = StoreSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

        # Проверяю есть ли в базе пользователь, назначенный хозяином магазина
        owner_id = request.data['owner']
        result = is_exists(owner_id, User)
        if not result:
            return Response(f'Please create user first', status=status.HTTP_400_BAD_REQUEST)
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(f'Store {serializer.validated_data["name"]} created successfully',
                                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # Проверка прав

        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

        # Проверяю есть ли в базе пользователь, назначенный хозяином магазина
        owner_id = request.data['owner']
        result = is_exists(owner_id, User)
        if not result:
            return Response(f'Please create user first', status=status.HTTP_400_BAD_REQUEST)
        # Проверяю есть ли указанный магазин в базе
        store_id = request.data['id']
        result = is_exists(store_id, Store)
        if not result:
            return Response(f'Please create store first', status=status.HTTP_400_BAD_REQUEST)
        serializer = StoreSerializer(result, data=request.data)
        if serializer.is_valid():
            serializer.update(result, request.data)
            if serializer.errors == {}:
                return Response(f'Store updated successfully', status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

        store_id = request.data['id']
        result = is_exists(store_id, Store)
        if result:
            result.delete()
            return Response(f'Store deleted successfully', status=status.HTTP_200_OK)
        return Response('Store not found', status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------Пользователи-------------------------------------
class UsersView(APIView):
    def get(self, request):
        queryset = User.objects.all()
        serializer = UserViewSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

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
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

        user_id = request.data['id']
        result = is_exists(user_id, User)
        if not result:
            return Response('User not found', status=status.HTTP_400_BAD_REQUEST)
        mutable_request = request.data.copy()
        mutable_request['password'] = encrypt_password(mutable_request['password'])
        mutable_request['token'] = generate_token()
        serializer = UserCreateSerializer(result, data=mutable_request)
        if serializer.is_valid():
            serializer.update(result, mutable_request)
            if serializer.errors == {}:
                return Response(f'User updated successfully', status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

        user_id = request.data['id']
        result = is_exists(user_id, User)
        if not result:
            return Response('User not found', status=status.HTTP_400_BAD_REQUEST)
        result.delete()
        return Response(f'User deleted successfully', status=status.HTTP_200_OK)


# ----------------------------------------------Товары------------------------------------------
class ProductsView(APIView):

    def get(self, request):
        queryset = Product.objects.all()
        serializer = ViewProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin', 'seller']):
            return Response('Admin or seller rights required', status=status.HTTP_400_BAD_REQUEST)

        category_id = request.data['category']
        result = is_exists(category_id, Category)
        if not result:
            return Response('Category not found', status=status.HTTP_400_BAD_REQUEST)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(f'Product {serializer.validated_data["name"]} created successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

        category_id = request.data['category']
        result = is_exists(category_id, Category)
        if not result:
            return Response('Category not found', status=status.HTTP_400_BAD_REQUEST)
        product_id = request.data['id']
        result = is_exists(product_id, Product)
        if not result:
            return Response('Product not found', status=status.HTTP_400_BAD_REQUEST)
        serializer = ProductSerializer(result, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(f'Product updated successfully', status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ['admin']):
            return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)

        product_id = request.data['id']
        result = is_exists(product_id, Product)
        if not result:
            return Response('Product not found', status=status.HTTP_400_BAD_REQUEST)
        result.delete()
        return Response(f'Product deleted successfully', status=status.HTTP_200_OK)


# ----------------------------------------------Товары в магазине------------------------------
# class ProductStoreViewSet(viewsets.ModelViewSet):
#     queryset = ProductStore.objects.all()
#     serializer_class = ProductStoreSerializer
#
#     def get_queryset(self, request):
#         store = request.query_params.get('store')
#         product = request.query_params.get('product')
#         if store is not None:
#             return ProductStore.objects.filter(store=store)
#         if product is not None:
#             return ProductStore.objects.filter(product=product)
#         return super().get_queryset()
class ProductStoreView(APIView):
    def get(self, request):
        # store = request.query_params.get('store')
        # product = request.query_params.get('product')
        # arg_1, arg_2 = None, None
        # if store is None and product is None:
        #     queryset = ProductStore.objects.all()
        #     serializer = ViewProductStoreSerializer(queryset, many=True)
        #     return Response(serializer.data)
        # if store is not None:
        #     store = get_id_by_name(store, Store)
        #     arg_1 = str(store)
        # if product is not None:
        #     product = get_id_by_name(product, Product)
        #     arg_2 = str(product)
        # queryset = ProductStore.objects.filter(Q(store=arg_1) & Q(product=arg_2))
        # serializer = ViewProductStoreSerializer(queryset, many=True)
        # return Response(serializer.data)

        store = request.query_params.get('store')
        product = request.query_params.get('product')
        if store is None and product is None:
            queryset = ProductStore.objects.all()
            serializer = ViewProductStoreSerializer(queryset, many=True)
            return Response(serializer.data)

        if store is not None and product is not None:
            store = get_id_by_name(store, Store)
            product = get_id_by_name(product, Product)
            queryset = ProductStore.objects.filter(store=store, product=product)
            serializer = ViewProductStoreSerializer(queryset, many=True)
            return Response(serializer.data)

        if product is None:
            store = get_id_by_name(store, Store)
            queryset = ProductStore.objects.filter(store=store)
            serializer = ViewProductStoreSerializer(queryset, many=True)
            return Response(serializer.data)

        product = get_id_by_name(product, Product)
        queryset = ProductStore.objects.filter(product=product)
        serializer = ViewProductStoreSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not (is_store_owner(request) or is_role(request, ['admin'])):
            return Response('You should be an owner or admin', status=status.HTTP_400_BAD_REQUEST)

        # проверяю на наличие товара в базе
        product_id = request.data['product']
        product = is_exists(product_id, Product)
        if not product:
            return Response('Please create product first', status=status.HTTP_400_BAD_REQUEST)

        # проверяю на наличие магазина в базе
        store_id = request.data['store']
        store = is_exists(store_id, Store)
        if not store:
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
        return Response('Product added to store', status=status.HTTP_201_CREATED)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not (is_store_owner(request) or is_role(request, ['admin'])):
            return Response('You should be an owner or admin', status=status.HTTP_400_BAD_REQUEST)

        # проверяю на наличие товара в базе
        product_id = request.data['product']
        product = is_exists(product_id, Product)
        if not product:
            return Response('Product not found', status=status.HTTP_400_BAD_REQUEST)
        # проверяю на наличие магазина в базе
        store_id = request.data['store']
        store = is_exists(store_id, Store)
        if not store:
            return Response('Store not found', status=status.HTTP_400_BAD_REQUEST)
        # Проверка на наличие товара в магазине
        try:
            product_in_store = ProductStore.objects.get(product=product, store=store)
        except ObjectDoesNotExist:
            return Response(f'No product in store', status=status.HTTP_400_BAD_REQUEST)

        # Проверка - удалить всю позицию или только несколько товаров
        if request.data['delete_product'].upper() == 'YES':
            product_in_store.delete()
            return Response(f'Product deleted from store successfully',
                            status=status.HTTP_200_OK)
        else:
            quantity = request.data['quantity']
            in_store = ProductStore.objects.get(product=product_id, store=store_id).quantity
            if quantity > in_store:
                return Response(f'Cannot delete {quantity} items as only {in_store} is in store',
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                product_in_store.quantity = in_store - quantity
                product_in_store.save(update_fields=['quantity'])
        return Response(f'Product deleted from store successfully', status=status.HTTP_200_OK)

    def patch(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f'Wrong token', status=status.HTTP_404_NOT_FOUND)
        if not (is_store_owner(request) or is_role(request, ['admin'])):
            return Response('You should be an owner or admin', status=status.HTTP_400_BAD_REQUEST)

        # проверяю на наличие товара в базе
        product_id = request.data['product']
        product = is_exists(product_id, Product)
        if not product:
            return Response('Product not found', status=status.HTTP_400_BAD_REQUEST)
        # проверяю на наличие магазина в базе
        store_id = request.data['store']
        store = is_exists(store_id, Store)
        if not store:
            return Response('Store not found', status=status.HTTP_400_BAD_REQUEST)
        # Проверка на наличие товара в магазине
        try:
            product_in_store = ProductStore.objects.get(product=product, store=store)
        except ObjectDoesNotExist:
            return Response(f'No product in store', status=status.HTTP_400_BAD_REQUEST)

        product_in_store.quantity = request.data['quantity']
        product_in_store.price = request.data['price']
        product_in_store.product = product
        product_in_store.store = store
        product_in_store.save(update_fields=['quantity', 'price', 'product', 'store'])
        return Response(f'Product updated', status=status.HTTP_202_ACCEPTED)


# ---------------------------------------------------Заказы------------------------------------
# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = ViewOrderSerializer


class OrdersView(APIView):

    def get(self, request):
        user = request.query_params.get('user')
        status = request.query_params.get('product')
        if user is None and status is None:
            queryset = Order.objects.all()
            serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data)

        if user is not None and status is not None:
            store = get_id_by_name(user, User)
            queryset = Order.objects.filter(user=user, status=status)
            serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data)

        if user is None:
            queryset = Order.objects.filter(status=status)
            serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data)

        user = get_id_by_name(user, User)
        queryset = Order.objects.filter(user=user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)
#
    def post(self, request):

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
