from rest_framework import serializers

from backend.models import ProductStore

class ProductStoreSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    store_name = serializers.CharField(source='store.name')
    class Meta:
        model = ProductStore
        fields = ('id', 'product', 'product_name', 'store', 'store_name', 'quantity', 'price')
