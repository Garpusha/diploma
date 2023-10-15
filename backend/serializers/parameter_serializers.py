from rest_framework import serializers
from rest_framework.relations import StringRelatedField

from backend.models import Parameter, Product


class ParameterSerializer(serializers.ModelSerializer):
    product = StringRelatedField(read_only=True)

    class Meta:
        model = Parameter
        fields = ('id', 'name', 'value', 'product', )
