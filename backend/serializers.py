from rest_framework import serializers

from backend.models import Category, Store, User, Product, ProductStore, Parameter, Order, OrderProduct


# Вывод категорий
class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name')


# Вывод магазинов
class StoreSerializer(serializers.ModelSerializer):
    product_field = serializers.SerializerMethodField(read_only=True)
    # owner = serializers.SerializerMethodField(read_only=True)
    owner = serializers.CharField(source='user.name', read_only=True)
    class Meta:
        model = Store
        fields = ('id', 'name', 'owner', 'delivery_cost', 'product_field')



    def get_owner(self, queryset):
        owner_name = User.objects.get(id=queryset.owner_id).name
        return owner_name

    def get_product_field(self, obj):

        product_data = ProductStore.objects.filter(store=obj.id).values_list('product', flat=True)
        required_data = [list(Product.objects.filter(id=product).values()) for product in product_data]
        return required_data


# Вывод при создании пользователя
class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'password', 'role', 'email',
                  'address_1', 'address_2', 'address_3',
                  'address_4', 'address_5', )


# Вывод пользователей
class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'role', 'email', 'address_1',
                  'address_2', 'address_3', 'address_4', 'address_5', )


# Вывод параметров
class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('id', 'product', 'name', 'value')


class ProductParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('name', 'value')

# Вывод товаров
class ProductSerializer(serializers.ModelSerializer):

    parameters = ProductParameterSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'parameters', 'description')



# Вывод товаров в магазине
class ProductStoreSerializer(serializers.ModelSerializer):


    # делать нормальный вывод по магазинам

    # product = ProductSerializer()
    product = serializers.CharField(source='product.name')
    store = serializers.CharField(source='store.name')
    # store = StoreSerializer()

    class Meta:

        model = ProductStore
        fields = ('id', 'product', 'store', 'quantity', 'price')


# Детали заказа
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.name', read_only=True)
    items_cost = serializers.SerializerMethodField(read_only=True)
    delivery_cost = serializers.SerializerMethodField(read_only=True)
    product = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Order
        fields = ('id', 'user', 'items_cost', 'delivery_cost', 'status', 'created_at', 'product')

    def get_product(self, queryset):

        # Получаю queryset по id заказа
        required_data = list(OrderProduct.objects.filter(order=queryset.id).values())
        result = []

        # пробегаю по всем товарам в заказе, собираю итоговый queryset добавляя и удаляя поля
        for count, item in enumerate(required_data):
            product_id = required_data[count]['product_id']
            store_id = required_data[count]['store_id']
            [required_data[count].pop(key) for key in ('id', 'order_id', 'product_id', 'store_id')]
            product = list(Product.objects.filter(id=product_id).values())
            required_data[count]['product_name'] = product[0]['name']
            required_data[count]['store'] = list(Store.objects.filter(id=store_id).values())[0]['name']
            result.append(required_data[count])
        return result

    def get_items_cost(self, queryset):
        return 0

    def get_delivery_cost(self, queryset):
        return 0


