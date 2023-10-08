from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from.models import User
from.serializers import UserViewSerializer, UserCreateSerializer
from.functions import encrypt_password

class UsersView(APIView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserViewSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        mutable_request = request.data.copy()
        if mutable_request['password_1'] == mutable_request['password_2']:
            mutable_request['password'] = encrypt_password(mutable_request['password_1'])
            del mutable_request['password_1']
            del mutable_request['password_2']
        else:
            return Response('Passwords do not match', status=status.HTTP_400_BAD_REQUEST)
        serializer = UserCreateSerializer(data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            return Response(f'User {serializer.validated_data["name"]} created successfully', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
