from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from.models import User
from.serializers import UserSerializer
from.functions import encrypt_password

class UsersView(APIView):
    def get(self, request, *args, **kwargs):
        # User.objects.create(name='Test User', email='kenaa@example.com', password='testpwd', role='test_role', address_1='test_address_1', address_2='test_address_2')
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
