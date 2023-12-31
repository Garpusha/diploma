from rest_framework import serializers

from backend.functions import total_items_cost, total_delivery_cost
from backend.models import (
    Category,
    Store,
    User,
    Product,
    ProductStore,
    Parameter,
    Order,
    OrderProduct,
    ProductParameter,
)


# --------------------------------------------------Категории---------------------------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


# --------------------------------------------------Магазины---------------------------------------------
# Вывод магазинов
class ViewStoreSerializer(serializers.ModelSerializer):
    product_field = serializers.SerializerMethodField(read_only=True)
    # owner = serializers.SerializerMethodField(read_only=True)
    owner = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model = Store
        fields = ("id", "name", "owner", "delivery_cost", "active", "product_field")

    def get_owner(self, queryset):
        owner_name = User.objects.get(id=queryset.owner_id).name
        return owner_name

    def get_product_field(self, obj):
        product_data = ProductStore.objects.filter(store=obj.id).values_list(
            "product", flat=True
        )
        required_data = [
            list(Product.objects.filter(id=product).values())
            for product in product_data
        ]
        return required_data


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.id = validated_data.get("id", instance.id)
        instance.name = validated_data.get("name", instance.name)
        instance.owner = User.objects.get(id=validated_data["owner"])
        instance.active = validated_data.get("active", instance.active)
        instance.delivery_cost = validated_data.get(
            "delivery_cost", instance.delivery_cost
        )
        instance.save()
        return instance


# --------------------------------------------------Пользователи--------------------------------------------
# Вывод при создании пользователя
class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


# Вывод пользователей
class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "role",
            "email",
            "address_1",
            "address_2",
            "address_3",
            "address_4",
            "address_5",
        )


# --------------------------------------------------Параметры---------------------------------------------
class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ("id", "name")


class ProductParameterSerializer(serializers.ModelSerializer):
    # product = serializers.CharField(source='product.name')
    # parameter = serializers.CharField(source='parameter.name')

    class Meta:
        model = ProductParameter
        fields = ("id", "product", "parameter", "value")


class ViewProductParameterSerializer(serializers.ModelSerializer):
    # product = serializers.CharField(source='product.name')
    parameter = serializers.CharField(source="parameter.name")

    class Meta:
        model = ProductParameter
        fields = ("id", "parameter", "value")


# --------------------------------------------------Товары---------------------------------------------
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "category", "description")


class ViewProductSerializer(serializers.ModelSerializer):
    parameters = ViewProductParameterSerializer(many=True, read_only=True)
    category = serializers.CharField(source="category.name")

    class Meta:
        model = Product
        fields = ("id", "name", "category", "parameters", "description")


# --------------------------------------------------Товары в заказе---------------------------------------------
class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = "__all__"


# Вывод товаров в магазине
class ProductStoreSerializer(serializers.ModelSerializer):
    # product = serializers.CharField(source='product.name')
    # store = serializers.CharField(source='store.name')

    class Meta:
        model = ProductStore
        fields = ("id", "product", "store", "quantity", "price")


class ViewProductStoreSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name")
    store = serializers.CharField(source="store.name")

    class Meta:
        model = ProductStore
        fields = ("id", "product", "store", "quantity", "price")


class OrderSerializer(serializers.ModelSerializer):
    # user = serializers.CharField(source='user.name', read_only=True)
    class Meta:
        model = Order
        fields = ("id", "user", "status")


# Детали заказа
class ViewOrderSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.name", read_only=True)
    items_cost = serializers.SerializerMethodField(read_only=True)
    delivery_cost = serializers.SerializerMethodField(read_only=True)
    product = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "items_cost",
            "delivery_cost",
            "status",
            "created_at",
            "product",
        )

    def get_product(self, queryset):
        # Получаю queryset по id заказа
        required_data = list(OrderProduct.objects.filter(order=queryset.id).values())
        result = []

        # пробегаю по всем товарам в заказе, собираю итоговый queryset добавляя и удаляя поля
        for count, item in enumerate(required_data):
            product_id = required_data[count]["product_id"]
            store_id = required_data[count]["store_id"]
            [
                required_data[count].pop(key)
                for key in ("order_id", "product_id", "store_id")
            ]
            product = list(Product.objects.filter(id=product_id).values())
            required_data[count]["product_name"] = product[0]["name"]
            required_data[count]["store"] = list(
                Store.objects.filter(id=store_id).values()
            )[0]["name"]
            result.append(required_data[count])
        return result

    def get_items_cost(self, queryset):
        return total_items_cost(queryset)

    def get_delivery_cost(self, queryset):
        return total_delivery_cost(queryset)
