from backend.functions import read_yaml, import_data, encrypt_password, generate_token
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
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        match request.data['method']:
            case 'patch':
                result = self.patch(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'delete':
                result = self.delete(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'post':
                serializer = CategorySerializer(data=request.data.copy())
                if serializer.is_valid():
                    serializer.save()
                    return Response(f'Category {serializer.validated_data["name"]} created successfully',
                                    status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        old_category = request.data.get('name', None)
        new_category = request.data.get('newname', None)
        category = Category.objects.get(name=old_category)
        mutable_request = request.data.copy()
        mutable_request['name'] = new_category
        del mutable_request['newname']
        serializer = CategorySerializer(category, data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            return Response(f'Category {serializer.validated_data["name"]} updated successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        categoryname = request.data.get('name', None)
        category = Category.objects.get(name=categoryname)
        category.delete()
        return Response(f'Category {categoryname} deleted successfully',
                        status=status.HTTP_201_CREATED)


# ---------------------------------------------Параметры----------------------------------------
class ParametersView(APIView):
    def get(self, request, *args, **kwargs):
        parameters = Parameter.objects.all()
        serializer = ParameterSerializer(parameters, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        match request.data['method']:
            case 'patch':
                result = self.patch(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'delete':
                result = self.delete(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'post':
                serializer = ParameterSerializer(data=request.data.copy())
                if serializer.is_valid():
                    serializer.save()
                    return Response(f'Parameter created successfully',
                                    status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        old_category = request.data.get('name', None)
        new_category = request.data.get('newname', None)
        parameter = Parameter.objects.get(name=old_category)
        mutable_request = request.data.copy()
        mutable_request['name'] = new_category
        del mutable_request['newname']
        serializer = ParameterSerializer(parameter, data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            return Response(f'Parameter updated successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        product = request.data.get('product_id', None)
        parametername = request.data.get('name', None)
        parameter = Parameter.objects.get(name=parametername, id=product)
        parameter.delete()
        return Response(f'Parameter deleted successfully',
                        status=status.HTTP_201_CREATED)


# ----------------------------------------------Магазины----------------------------------------
class StoresView(APIView):
    def get(self, request, *args, **kwargs):
        stores = Store.objects.all()
        serializer = ViewStoreSerializer(stores, many=True, )
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        match request.data['method']:
            case 'patch':
                result = self.patch(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'delete':
                result = self.delete(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'post':
                try:
                    owner = User.objects.get(name=request.data['owner'])
                except ObjectDoesNotExist:
                    return Response('Please create product first', status=status.HTTP_400_BAD_REQUEST)
                owner_id = owner.id
                mutable_request = request.data.copy()
                mutable_request['owner'] = owner_id
                store = Store.objects.create(owner=owner, name=request.data['name'], delivery_cost=request.data['delivery_cost'])
                store.save()
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)
        return Response(f'Store {store.name} added successfully',
                        status=status.HTTP_201_CREATED)
    def patch(self, request, *args, **kwargs):
        oldname = request.data.get('name', None)
        newname = request.data.get('newname', None)
        delivery_cost = request.data.get('delivery_cost', None)
        mutable_request = request.data.copy()
        if newname is not None:
            mutable_request['name'] = newname
        del mutable_request['newname']
        if delivery_cost is not None:
            mutable_request['delivery_cost'] = delivery_cost
        store = Store.objects.get(name=oldname)
        serializer = ViewStoreSerializer(store, data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            return Response(f'Store {serializer.validated_data["name"]} updated successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        storename = request.data.get('name', None)
        store = Store.objects.get(name=storename)
        store.delete()
        return Response(f'Store {storename} deleted successfully',
                        status=status.HTTP_201_CREATED)


# ---------------------------------------------Пользователи-------------------------------------
class UsersView(APIView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserViewSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        match request.data['method']:
            case 'patch':
                result = self.patch(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'delete':
                result = self.delete(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'post':
                mutable_request = request.data.copy()
                if mutable_request['password_1'] == mutable_request['password_2']:
                    mutable_request['password'] = encrypt_password(mutable_request['password_1'])
                    del mutable_request['password_1']
                    del mutable_request['password_2']
                else:
                    return Response('Passwords do not match', status=status.HTTP_400_BAD_REQUEST)
                mutable_request['token'] = generate_token()
                serializer = UserCreateSerializer(data=mutable_request)
                if serializer.is_valid():
                    serializer.save()
                    return Response(f'User {serializer.validated_data["name"]} created successfully, token is \
                        {mutable_request["token"]}', status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        password = encrypt_password(request.data.get('password', None))
        username = request.data.get('name', None)
        user = User.objects.get(name=username)
        stored_password = user.password
        if password != stored_password:
            return Response('Wrong password', status=status.HTTP_400_BAD_REQUEST)
        mutable_request = request.data.copy()
        mutable_request['password'] = password
        serializer = UserCreateSerializer(user, data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            return Response(f'User {serializer.validated_data["name"]} updated successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        password = encrypt_password(request.data.get('password', None))
        username = request.data.get('name', None)
        user = User.objects.get(name=username)
        stored_password = user.password
        if password != stored_password:
            return Response('Wrong password', status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response(f'User {username} deleted successfully',
                        status=status.HTTP_201_CREATED)


# ----------------------------------------------Товары------------------------------------------
class ProductsView(APIView):

    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        serializer = ViewProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        match request.data['method']:
            case 'patch':
                result = self.patch(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'delete':
                result = self.delete(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'post':
                mutable_request = request.data.copy()
                category = mutable_request.get('category', None)
                category_id = Category.objects.get(name=category).id
                if category_id is None:
                    return Response('Wrong category', status=status.HTTP_400_BAD_REQUEST)
                mutable_request['category'] = category_id
                serializer = ProductSerializer(data=mutable_request)
                if serializer.is_valid():
                    serializer.save()
                    return Response(f'Product {serializer.validated_data["name"]} created successfully',
                                    status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        product_id = request.data.get('id', None)
        mutable_request = request.data.copy()
        product = Product.objects.get(id=product_id)
        category = mutable_request.get('category', None)
        category_id = Category.objects.get(name=category).id
        if category_id is None:
            return Response('Wrong category', status=status.HTTP_400_BAD_REQUEST)
        mutable_request['category_id'] = category_id
        del mutable_request['category']
        serializer = ProductSerializer(product, data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            return Response(f'Product {serializer.validated_data["name"]} updated successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('id', None)
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response(f'Product deleted successfully',
                        status=status.HTTP_201_CREATED)


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

    #             считать общую стоимость заказа

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
            user['token'] = generate_token()

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
