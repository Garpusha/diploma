from rest_framework import serializers

from backend.models import Order, OrderProduct


class OrderProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderProduct
        fields = ('product_name', 'store', 'quantity', 'price')


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'total_cost', 'status', 'created_at', 'products')
