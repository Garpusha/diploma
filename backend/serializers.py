from rest_framework import serializers

from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'password', 'role', 'email',
                  'address_1', 'address_2', 'address_3',
                  'address_4', 'address_5', )

class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'role', 'email', 'address_1',
                  'address_2', 'address_3', 'address_4', 'address_5', )
