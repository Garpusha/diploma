from rest_framework import serializers

from backend.models import Category, Store, User, Product, ProductStore, Basket, OrderedPosition, Parameter, Order, \
    OrderedPositions


# Вывод категорий
class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name')


# Вывод магазинов
class StoreSerializer(serializers.ModelSerializer):
    product_field = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Store
        fields = ('id', 'name', 'delivery_cost', 'product_field')

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


# Вывод товаров
class ProductSerializer(serializers.ModelSerializer):

    parameters = ParameterSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'parameters', 'description')



# Вывод товаров в магазине
class ProductStoreSerializer(serializers.ModelSerializer):

    product = ProductSerializer()
    # product = serializers.CharField(source='product.name')
    # store = serializers.CharField(source='store.name')
    store = StoreSerializer()

    class Meta:

        # model = ProductStore
        fields = ('id', 'product', 'store', 'quantity', 'price')


# Детали заказа
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.name', read_only=True)
    items_cost = serializers.SerializerMethodField('get_items_cost')
    delivery_cost = serializers.SerializerMethodField('get_delivery_cost')

    class Meta:
        model = Order
        fields = ('id', 'user', 'items_cost', 'delivery_cost', 'status', 'created_at')

    def get_items_cost(self, order):
        return 0

    def get_delivery_cost(self, order):
        return 0


class OrderedPositionSerializer(serializers.ModelSerializer):

    product = serializers.CharField(source='product.name', read_only=True)
    store = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = OrderedPosition
        fields = ('product', 'store', 'quantity', 'price')


class OrderedPositionsSerializer(serializers.ModelSerializer):
    position = OrderedPositionSerializer()

    class Meta:
        model = OrderedPositions
        fields = ('order', 'position')


class BasketSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.name', read_only=True)
    order = OrderSerializer(read_only=True)
    positions = OrderedPositionsSerializer()

    class Meta:
        model = Basket
        fields = ('user', 'order', 'positions')
