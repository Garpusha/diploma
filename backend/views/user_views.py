from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import User
from backend.serializers.user_serializers import UserViewSerializer, UserCreateSerializer
from backend.functions import encrypt_password


class UsersView(APIView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserViewSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        match request.data['method']:
            case 'patch':
                result = self.patch(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'delete':
                result = self.delete(request, *args, **kwargs)
                return Response(result.data, status=result.status_code)
            case 'post':
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
                    return Response(f'User {serializer.validated_data["name"]} created successfully',
                                    status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)



    def patch(self, request, *args, **kwargs):
        password = encrypt_password(request.data.get('password', None))
        username = request.data.get('name', None)
        user = User.objects.get(name=username)
        stored_password = user.password
        if password != stored_password:
            return Response('Wrong password', status=status.HTTP_400_BAD_REQUEST)
        mutable_request = request.data.copy()
        mutable_request['password'] = password
        serializer = UserCreateSerializer(user, data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            return Response(f'User {serializer.validated_data["name"]} updated successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        password = encrypt_password(request.data.get('password', None))
        username = request.data.get('name', None)
        user = User.objects.get(name=username)
        stored_password = user.password
        if password != stored_password:
            return Response('Wrong password', status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response(f'User {username} deleted successfully',
                        status=status.HTTP_201_CREATED)