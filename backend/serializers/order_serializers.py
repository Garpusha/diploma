from rest_framework import serializers

from backend.models import Order, OrderProduct


class OrderSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)


    class Meta:
        model = Order
        fields = ('id', 'user', 'user_name', 'status', 'created_at')


class OrderProductSerializer(serializers.ModelSerializer):
    # queryset = OrderProduct.objects.all()
    order = OrderSerializer()
    total_cost = serializers.SerializerMethodField('get_total_cost')
    product_name = serializers.CharField(source='product.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    def get_total_cost(self, order):
        return 0

    class Meta:
        model = OrderProduct
        fields = ('order', 'store', 'store_name', 'product', 'product_name', 'quantity', 'price', 'total_cost')

        # model = Order
        # fields = ('id', 'user', 'total_cost', 'status', 'created_at', 'product')
