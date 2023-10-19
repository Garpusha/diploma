from rest_framework import serializers

from backend.models import ProductStore

class ProductStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStore
        fields = ('id', 'product', 'store', 'quantity', 'price')
