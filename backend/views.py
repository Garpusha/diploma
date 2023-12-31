from backend.functions import (
    read_yaml,
    import_data,
    encrypt_password,
    generate_token,
    is_exists,
    is_token_exists,
    is_role,
    is_store_owner,
    get_object_by_name,
    check_balance,
    delete_from_store,
    generate_order_msg,
    generate_token_msg,
    send_email, generate_seller_msg
)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import (
    Category,
    Parameter,
    Store,
    User,
    Product,
    ProductStore,
    Order,
    OrderProduct, ProductParameter,
)
from backend.serializers import (
    CategorySerializer,
    ParameterSerializer,
    StoreSerializer,
    UserViewSerializer,
    UserCreateSerializer,
    ProductSerializer,
    ProductStoreSerializer,
    OrderSerializer,
    ProductParameterSerializer,
    OrderProductSerializer,
    ViewOrderSerializer,
    ViewProductStoreSerializer,
    ViewProductSerializer,
)


# --------------------------------------------Авторизация-----------------------------------------
class AuthorizationView(APIView):
    def post(self, request):
        user = get_object_by_name(request.data["username"], User)
        if not user:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)

        # По запросу с "operation": "authorize" можно получить новый токен, указав верный пароль
        # Если пользователь забыл пароль, по запросу "operation": "reset" ему на почту высылается
        # новый токен. По запросу "operation": "activate" с новым токеном можно установить новый пароль
        operation = request.data["operation"].lower()
        match operation:
            case "authorize":
                password = encrypt_password(request.data["password"])
                if password == user.password:
                    user.token = generate_token()
                    user.save(update_fields=["token"])
                    return Response(
                        f"Authorization ok, your new token is: {user.token}",
                        status=status.HTTP_200_OK,
                    )
                return Response("Wrong password", status=status.HTTP_400_BAD_REQUEST)
            case "reset":
                user.temp_token = generate_token()
                user.save(update_fields=["temp_token"])
                msg = generate_token_msg(user)
                send_email(send_to=user.email,
                           subject="Password reset",
                           message=msg
                           )
                return Response("New token was sent to your e-mail", status=status.HTTP_200_OK)
            case "activate":
                token = request.headers["Authorization"][6:]
                if user.temp_token != token:
                    return Response("Wrong token", status=status.HTTP_400_BAD_REQUEST)
                user.token = user.temp_token
                user.temp_token = ""
                user.password = encrypt_password(request.data['password'])
                user.save(update_fields=["token", "temp_token", "password"])
                return Response("Password updated successfully", status=status.HTTP_200_OK)
        return Response("Wrong operation", status=status.HTTP_400_BAD_REQUEST)


# --------------------------------------------Категории-----------------------------------------
class CategoriesView(APIView):
    def get(self, request):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response("Admin rights required", status=status.HTTP_400_BAD_REQUEST)

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(
                    f'Category {serializer.validated_data["name"]} created successfully',
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response("Admin rights required", status=status.HTTP_400_BAD_REQUEST)

        category_name = request.data["name"]
        category = get_object_by_name(category_name, Category)
        if not category:
            return Response("Category not found", status=status.HTTP_400_BAD_REQUEST)
        if category:
            category.delete()
            return Response(f"Category deleted successfully", status=status.HTTP_200_OK)
        return Response(f"Category not found", status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response("Admin rights required", status=status.HTTP_400_BAD_REQUEST)

        serializer = CategorySerializer(data=request.data)
        category_id = request.data["id"]
        result = is_exists(category_id, Category)
        if not result:
            return Response(f"Category not found", status=status.HTTP_404_NOT_FOUND)
        if serializer.is_valid():
            serializer.update(result, request.data)
            if serializer.errors == {}:
                return Response(
                    f"Category updated successfully", status=status.HTTP_202_ACCEPTED
                )
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
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin", "seller"]):
            return Response(
                "Admin or seller rights required", status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ParameterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(
                    f'Parameter {serializer.validated_data["name"]} created successfully',
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response("Admin rights required", status=status.HTTP_400_BAD_REQUEST)

        parameter_id = request.data["id"]
        result = is_exists(parameter_id, Parameter)
        if result:
            result.delete()
            return Response(
                f"Parameter deleted successfully", status=status.HTTP_200_OK
            )
        return Response(f"Parameter not found", status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response("Admin rights required", status=status.HTTP_400_BAD_REQUEST)

        serializer = ParameterSerializer(data=request.data)
        parameter_id = request.data["id"]
        result = is_exists(parameter_id, Parameter)
        if not result:
            return Response(f"Parameter not found", status=status.HTTP_404_NOT_FOUND)
        if serializer.is_valid():
            serializer.update(result, request.data)
            if serializer.errors == {}:
                return Response(
                    f"Parameter updated successfully", status=status.HTTP_202_ACCEPTED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------------------------Параметры продуктов----------------------------------------
class ProductParametersView(APIView):
    def get(self, request):
        queryset = ProductParameter.objects.all()
        serializer = ProductParameterSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin", "seller"]):
            return Response(
                "Admin or seller rights required", status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ProductParameterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(
                    f'Parameter added successfully',
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response("Admin rights required", status=status.HTTP_400_BAD_REQUEST)

        pp_id = request.data["id"]
        result = is_exists(pp_id, ProductParameter)
        if result:
            result.delete()
            return Response(
                f"Parameter deleted successfully", status=status.HTTP_200_OK
            )
        return Response(f"Parameter not found", status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response("Admin rights required", status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductParameterSerializer(data=request.data)
        pp_id = request.data["id"]
        pp = is_exists(pp_id, ProductParameter)
        if not pp:
            return Response(f"Parameter relation not found", status=status.HTTP_404_NOT_FOUND)
        parameter_id = request.data['parameter']
        parameter = is_exists(parameter_id, Parameter)
        if not parameter:
            return Response(f"Parameter not found", status=status.HTTP_404_NOT_FOUND)
        product_id = request.data['product']
        product =  is_exists(product_id, Product)
        if not product:
            return Response(f"Product not found", status=status.HTTP_404_NOT_FOUND)
        mutable_request = request.data.copy()
        mutable_request['product'] = product
        mutable_request['parameter'] = parameter
        if serializer.is_valid():
            serializer.update(pp, mutable_request)
            if serializer.errors == {}:
                return Response(
                    f"Product parameter updated successfully", status=status.HTTP_202_ACCEPTED
                )
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
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response("Admin rights required", status=status.HTTP_400_BAD_REQUEST)

        # Проверяю есть ли в базе пользователь, назначенный хозяином магазина
        owner_id = request.data["owner"]
        result = is_exists(owner_id, User)
        if not result:
            return Response(
                f"Please create user first", status=status.HTTP_400_BAD_REQUEST
            )
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(
                    f'Store {serializer.validated_data["name"]} created successfully',
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        store_id = request.data["id"]
        if not (is_store_owner(request, store_id) or is_role(request, ["admin"])):
            return Response(
                "You should be an owner or admin", status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяю есть ли в базе пользователь, назначенный хозяином магазина
        owner_id = request.data["owner"]
        owner = is_exists(owner_id, User)
        if not owner:
            return Response(
                f"Please create user first", status=status.HTTP_400_BAD_REQUEST
            )
        # Проверяю есть ли указанный магазин в базе
        store_id = request.data["id"]
        store = is_exists(store_id, Store)
        request.data["active"] = bool(request.data["active"])
        request.data["owner"] = owner_id
        if not store:
            return Response(
                f"Please create store first", status=status.HTTP_400_BAD_REQUEST
            )
        serializer = StoreSerializer(store, data=request.data)
        if serializer.is_valid():
            serializer.update(store, request.data)
            if serializer.errors == {}:
                return Response(
                    f"Store updated successfully", status=status.HTTP_202_ACCEPTED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response("Admin rights required", status=status.HTTP_400_BAD_REQUEST)

        store_id = request.data["id"]
        result = is_exists(store_id, Store)
        if result:
            result.delete()
            return Response(f"Store deleted successfully", status=status.HTTP_200_OK)
        return Response("Store not found", status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------Пользователи-------------------------------------
class UsersView(APIView):
    def get(self, request):
        queryset = User.objects.all()
        serializer = UserViewSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response("Admin rights required", status=status.HTTP_400_BAD_REQUEST)
        mutable_request = request.data.copy()
        mutable_request["password"] = encrypt_password(mutable_request["password"])
        mutable_request["token"] = generate_token()
        serializer = UserCreateSerializer(data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(
                    f'User {mutable_request["name"]} created successfully, token is:{mutable_request["token"]}',
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # Проверка прав

        user = is_token_exists(request)
        if not user:
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if user.name != request.data["name"]:
            if not is_role(request, ["admin"]):
                return Response(
                    "Authorization failed", status=status.HTTP_400_BAD_REQUEST
                )
            else:
                user = get_object_by_name(request.data["name"], User)
                if not user:
                    return Response("User not found", status=status.HTTP_404_NOT_FOUND)
        new_email = request.data["email"]
        # Если задан уже существующий email другого пользователя, обновления не произойдет
        if new_email.lower() != user.email.lower():
            result = User.objects.filter(email=new_email)
            if len(result) != 0:
                return Response(
                    "User with this email already exists",
                    status=status.HTTP_400_BAD_REQUEST,
                )

        mutable_request = request.data.copy()
        mutable_request["password"] = encrypt_password(mutable_request["password"])
        serializer = UserCreateSerializer(user, data=mutable_request)
        if serializer.is_valid():
            serializer.update(user, mutable_request)
            if serializer.errors == {}:
                return Response(
                    f"User {mutable_request['name']} updated successfully",
                    status=status.HTTP_202_ACCEPTED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response(
                "Authorization failed. Admin rights required.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_by_name(request.data["name"], User)
        if not user:
            return Response(
                f"User {request.data['name']} not found",
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.delete()
        return Response(
            f"User {request.data['name']} deleted successfully",
            status=status.HTTP_200_OK,
        )


# ----------------------------------------------Товары------------------------------------------
class ProductsView(APIView):
    def get(self, request):
        queryset = Product.objects.all()
        serializer = ViewProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin", "seller"]):
            return Response(
                "Admin or seller rights required", status=status.HTTP_400_BAD_REQUEST
            )

        category_id = request.data["category"]
        result = is_exists(category_id, Category)
        if not result:
            return Response("Category not found", status=status.HTTP_400_BAD_REQUEST)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                f'Product {serializer.validated_data["name"]} created successfully',
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response("Admin rights required", status=status.HTTP_400_BAD_REQUEST)

        category_id = request.data["category"]
        result = is_exists(category_id, Category)
        if not result:
            return Response("Category not found", status=status.HTTP_400_BAD_REQUEST)
        product_id = request.data["id"]
        result = is_exists(product_id, Product)
        if not result:
            return Response("Product not found", status=status.HTTP_400_BAD_REQUEST)
        serializer = ProductSerializer(result, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if serializer.errors == {}:
                return Response(
                    f"Product updated successfully", status=status.HTTP_202_ACCEPTED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response("Admin rights required", status=status.HTTP_400_BAD_REQUEST)

        product_id = request.data["id"]
        result = is_exists(product_id, Product)
        if not result:
            return Response("Product not found", status=status.HTTP_400_BAD_REQUEST)
        result.delete()
        return Response(f"Product deleted successfully", status=status.HTTP_200_OK)


# ----------------------------------------------Товары в магазине------------------------------
class ProductStoreView(APIView):
    def get(self, request):
        active_stores = Store.objects.filter(active=True)
        store = request.query_params.get("store")
        product = request.query_params.get("product")
        if store is None and product is None:
            queryset = ProductStore.objects.filter(store__in=active_stores)
            serializer = ViewProductStoreSerializer(queryset, many=True)
            return Response(serializer.data)

        if store is not None and product is not None:
            store_id = get_object_by_name(store, Store).id
            product_id = get_object_by_name(product, Product).id
            queryset = ProductStore.objects.filter(
                store=store_id, store_id__in=active_stores, product=product_id
            )
            serializer = ViewProductStoreSerializer(queryset, many=True)
            return Response(serializer.data)

        if product is None:
            store_id = get_object_by_name(store, Store).id
            queryset = ProductStore.objects.filter(
                store=store_id, store_id__in=active_stores
            )
            serializer = ViewProductStoreSerializer(queryset, many=True)
            return Response(serializer.data)

        product_id = get_object_by_name(product, Product).id
        queryset = ProductStore.objects.filter(
            product=product_id, store_id__in=active_stores
        )
        serializer = ViewProductStoreSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        store_id = request.data["store"]
        if not (is_store_owner(request, store_id) or is_role(request, ["admin"])):
            return Response(
                "You should be an owner or admin", status=status.HTTP_400_BAD_REQUEST
            )

        # проверяю на наличие товара в базе
        product_id = request.data["product"]
        product = is_exists(product_id, Product)
        if not product:
            return Response(
                "Please create product first", status=status.HTTP_400_BAD_REQUEST
            )

        # проверяю на наличие магазина в базе
        store_id = request.data["store"]
        store = is_exists(store_id, Store)
        if not store:
            return Response(
                "Please create store first", status=status.HTTP_400_BAD_REQUEST
            )

        quantity_value = int(request.data["quantity"])
        price_value = float(request.data["price"])

        # Считываю количество товаров в магазине, если таких товаров в этом магазине нет,
        # создаю нулевую запись, иначе прибавляю количество к уже имеющимся
        try:
            products_in_store = ProductStore.objects.get(product=product, store=store)
            in_stock = products_in_store.quantity
            current_price = float(products_in_store.price)
        except ObjectDoesNotExist:
            products_in_store = ProductStore.objects.create(
                product=product, store=store, quantity=0, price=0
            )
            products_in_store.save()
            in_stock = 0
            current_price = 0

        products_in_store.quantity = quantity_value + in_stock

        # Цена на складе усредняется с новой поставкой для упрощения
        products_in_store.price = (
            price_value * quantity_value + current_price * in_stock
        ) / (quantity_value + in_stock)
        products_in_store.save(update_fields=["quantity", "price"])
        return Response("Product added to store", status=status.HTTP_201_CREATED)

    def delete(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        store_id = request.data["store"]
        if not (is_store_owner(request, store_id) or is_role(request, ["admin"])):
            return Response(
                "You should be an owner or admin", status=status.HTTP_400_BAD_REQUEST
            )

        # проверяю на наличие товара в базе
        product_id = request.data["product"]
        product = is_exists(product_id, Product)
        if not product:
            return Response("Product not found", status=status.HTTP_400_BAD_REQUEST)
        # проверяю на наличие магазина в базе
        store_id = request.data["store"]
        store = is_exists(store_id, Store)
        if not store:
            return Response("Store not found", status=status.HTTP_400_BAD_REQUEST)
        # Проверка на наличие товара в магазине
        try:
            product_in_store = ProductStore.objects.get(product=product, store=store)
        except ObjectDoesNotExist:
            return Response(f"No product in store", status=status.HTTP_400_BAD_REQUEST)

        # Проверка - удалить всю позицию или только несколько товаров
        if request.data["delete_product"].upper() == "YES":
            product_in_store.delete()
            return Response(
                f"Product deleted from store successfully", status=status.HTTP_200_OK
            )
        else:
            quantity = request.data["quantity"]
            in_store = ProductStore.objects.get(
                product=product_id, store=store_id
            ).quantity
            if quantity > in_store:
                return Response(
                    f"Cannot delete {quantity} items as only {in_store} is in store",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                product_in_store.quantity = in_store - quantity
                product_in_store.save(update_fields=["quantity"])
        return Response(
            f"Product deleted from store successfully", status=status.HTTP_200_OK
        )

    def patch(self, request):
        # Проверка прав
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        store_id = request.data["store"]
        if not (is_store_owner(request, store_id) or is_role(request, ["admin"])):
            return Response(
                "You should be an owner or admin", status=status.HTTP_400_BAD_REQUEST
            )

        # проверяю на наличие товара в базе
        product_id = request.data["product"]
        product = is_exists(product_id, Product)
        if not product:
            return Response("Product not found", status=status.HTTP_400_BAD_REQUEST)
        # проверяю на наличие магазина в базе
        store_id = request.data["store"]
        store = is_exists(store_id, Store)
        if not store:
            return Response("Store not found", status=status.HTTP_400_BAD_REQUEST)
        # Проверка на наличие товара в магазине
        try:
            product_in_store = ProductStore.objects.get(product=product, store=store)
        except ObjectDoesNotExist:
            return Response(f"No product in store", status=status.HTTP_400_BAD_REQUEST)

        product_in_store.quantity = request.data["quantity"]
        product_in_store.price = request.data["price"]
        product_in_store.product = product
        product_in_store.store = store
        product_in_store.save(update_fields=["quantity", "price", "product", "store"])
        return Response(f"Product updated", status=status.HTTP_202_ACCEPTED)


# ---------------------------------------------------Заказы------------------------------------
class OrdersView(APIView):
    def get(self, request):
        # Проверка прав. Только админ видит все заказы
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_400_BAD_REQUEST)
        if not is_role(request, ["admin"]):
            return Response(f"Admin rights reqired", status=status.HTTP_400_BAD_REQUEST)

        user = request.query_params.get("user")
        my_status = request.query_params.get("status")
        if user is None and my_status is None:
            queryset = Order.objects.all()
            serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data)

        if user is not None and my_status is not None:
            user_id = get_object_by_name(user, User).id
            queryset = Order.objects.filter(user=user_id, status=my_status)
            serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data)

        if user is None:
            queryset = Order.objects.filter(status=my_status)
            serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data)

        user_id = get_object_by_name(user, User).id
        queryset = Order.objects.filter(user=user_id)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав.
        user = is_token_exists(request)
        if not user:
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        order = is_exists(request.data["id"], Order)

        # Проверка наличия заказа, его статуса, хозяина заказа
        if not order:
            return Response(f"Order not found", status=status.HTTP_400_BAD_REQUEST)
        if order.status != "active":
            return Response(
                f"Active order not found", status=status.HTTP_400_BAD_REQUEST
            )
        if user != order.user:
            return Response(
                f"This is not your order", status=status.HTTP_400_BAD_REQUEST
            )

        # Остаток в магазинах мог измениться, проверяю.
        not_enough = check_balance(order)
        if not_enough:
            return Response(not_enough, status=status.HTTP_400_BAD_REQUEST)
        # Уменьшаю остаток по всем товарам из заказа в магазинах, меняю статус заказа, отправляю уведомление по почте
        msg = generate_order_msg(user, order)
        if not msg:
            return Response('Order is empty', status=status.HTTP_204_NO_CONTENT)

        send_email(
            send_to=user.email,
            subject=f"Your order {order.id} in our marketplace",
            message=msg,
        )
        # Отправляю письма хозяевам магазинов, из которых заказаны товары
        products_in_order = OrderProduct.objects.filter(order=order)
        sellers = set()
        [sellers.add(product.store) for product in products_in_order]
        for seller in sellers:
            msg = generate_seller_msg(seller, order)
            send_email(send_to=user.email,
                       subject='Products ordered',
                       message=msg
                       )
        delete_from_store(order)
        order.status = "completed"
        order.save()
        return Response("Your order complete", status=status.HTTP_200_OK)

    def patch(self, request):
        # Проверка прав.
        user = is_token_exists(request)
        if not user:
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        order = is_exists(request.data["id"], Order)

        # Проверка наличия заказа, его статуса, хозяина заказа
        if not order:
            return Response(f"Order not found", status=status.HTTP_400_BAD_REQUEST)
        if order.status != "active":
            return Response(
                f"Active order not found", status=status.HTTP_400_BAD_REQUEST
            )
        if user != order.user and not is_role(request, "admin"):
            return Response(
                f"This is not your order", status=status.HTTP_400_BAD_REQUEST
            )
        order.status = "canceled"
        order.save()
        return Response(f"Order {order.id} canceled", status=status.HTTP_200_OK)

    def delete(self, request):
        # Проверка прав.
        user = is_token_exists(request)
        if not user:
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        order = is_exists(request.data["id"], Order)

        # Проверка наличия заказа, его статуса, хозяина заказа
        if not order:
            return Response(f"Order not found", status=status.HTTP_400_BAD_REQUEST)
        if user != order.user and not is_role(request, "admin"):
            return Response(
                f"This is not your order", status=status.HTTP_400_BAD_REQUEST
            )
        order.delete()
        return Response(
            f'Order {request.data["id"]} deleted', status=status.HTTP_200_OK
        )


class CartView(APIView):
    def get(self, request):
        # Проверка прав. Админ видит все заказы, пользователь только свои
        user = is_token_exists(request)
        if not user:
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if is_role(request, ["admin"]):
            queryset = Order.objects.all()
            serializer = ViewOrderSerializer(queryset, many=True)
            return Response(serializer.data)
        try:
            order = Order.objects.get(user=user, status="active")
        except ObjectDoesNotExist:
            return Response("This user has no orders")
        serializer = ViewOrderSerializer(order)
        return Response(serializer.data)

    def post(self, request):
        # Проверка прав. Каждый пользователь создает свой заказ. Активный заказ одновременно только один
        user = is_token_exists(request)
        if not user:
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)

        # Проверка на корректный ввод количества товаров
        quantity = int(request.data["quantity"])
        if quantity < 1:
            return Response(
                "Quantity must be at least 1", status=status.HTTP_400_BAD_REQUEST
            )

        # проверяю на наличие товара в базе
        product_id = request.data["product"]
        product = is_exists(product_id, Product)
        if not product:
            return Response(
                "Please create product first", status=status.HTTP_400_BAD_REQUEST
            )

        # проверяю на наличие магазина в базе
        store_id = request.data["store"]
        store = is_exists(store_id, Store)
        if not store:
            return Response(
                "Please create store first", status=status.HTTP_400_BAD_REQUEST
            )

        # проверяю активен ли магазин
        if not store.active:
            return Response("This store is closed", status=status.HTTP_400_BAD_REQUEST)

        # Проверяю есть ли такой товар в магазине
        try:
            product_in_store = ProductStore.objects.get(product=product, store=store)
        except ObjectDoesNotExist:
            return Response(
                f"No product {product.name} in store {store.name}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Проверяю достаточно ли товара в магазине
        if quantity > product_in_store.quantity:
            return Response(
                f"Not enough {product.name} in store {store.name}",
                status=status.HTTP_400_BAD_REQUEST,
            )
        price = float(product_in_store.price)

        # Проверяю есть ли активный заказ от этого пользователя, если нет, создаю
        try:
            order = Order.objects.get(user=user, status="active")
        except ObjectDoesNotExist:
            order = Order.objects.create(user=user, status="active")
            order.save()

        # Добавляю выбранный товар в общий заказ. Если такой товар уже есть в заказе из этого магазина,
        # увеличиваю количество, если нет создаю
        try:
            ordered_product = OrderProduct.objects.get(
                order=order, product=product, store=store
            )
            ordered_product.quantity += quantity
            ordered_product.save()
        except ObjectDoesNotExist:
            ordered_product = OrderProduct.objects.create(
                order=order,
                product=product,
                store=store,
                quantity=quantity,
                price=price,
            )
            ordered_product.save()

        return Response(
            f"Product {product.name} in store {store.name} was added to order {order.id}"
        )

    def delete(self, request):
        # Проверка существует ли заказ
        order = is_exists(request.data["id"], Order)
        if not order:
            return Response(f"Order not found", status=status.HTTP_400_BAD_REQUEST)

        # Проверка прав. Вносить правки в заказ может только админ или хозяин заказа
        user = is_token_exists(request)
        if not user:
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not (is_role(request, "admin") or user == order.user):
            return Response(
                f"This is not your order", status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка на корректный ввод количества товаров
        quantity = int(request.data["quantity"])
        if quantity < 1:
            return Response("Quantity must be at least 1", status=status.HTTP_400_BAD)
        position = int(request.data["position"])

        # Проверка на наличие товара в заказе
        try:
            ordered_product = OrderProduct.objects.get(order=order, id=position)
        except ObjectDoesNotExist:
            return Response(
                "No such product in this order", status=status.HTTP_400_BAD_REQUEST
            )
        if quantity > ordered_product.quantity:
            return Response(
                f"Cannot delete {quantity} item, only {ordered_product.quantity} in order",
                status=status.HTTP_400_BAD_REQUEST,
            )
        if quantity == ordered_product.quantity:
            ordered_product.delete()
        else:
            ordered_product.quantity -= quantity
            ordered_product.save()
        return Response(f"Product deleted succesfully", status=status.HTTP_200_OK)


class ImportData(APIView):
    def post(self, request):
        # Проверка прав.
        if not is_token_exists(request):
            return Response(f"Wrong token", status=status.HTTP_404_NOT_FOUND)
        if not is_role(request, ["admin"]):
            return Response(
                "You should have admin rights to upload data.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        # filename = request.FILES['filename']
        filename = request.data["file"]
        loaded_data = read_yaml(filename)
        # если есть раздел с пользователями, шифрую пароли, создаю токены
        if "users" in loaded_data.keys():
            for user in loaded_data["users"]:
                for key, value in user.items():
                    value["password"] = encrypt_password(value["password"])
                    value["token"] = generate_token()

        dataset = {
            "users": UserCreateSerializer,
            "categories": CategorySerializer,
            "stores": StoreSerializer,
            "products": ProductSerializer,
            "parameters": ParameterSerializer,
            "orders": OrderSerializer,
            "product_parameters": ProductParameterSerializer,
            "products_in_store": ProductStoreSerializer,
            "products_in_order": OrderProductSerializer,
        }
        for key, value in dataset.items():
            try:
                my_response = import_data(loaded_data[key], value)
            except KeyError:
                continue
            if my_response != "ok":
                return my_response

        return Response(
            f"All data from {filename} uploaded successfully ",
            status=status.HTTP_201_CREATED,
        )
