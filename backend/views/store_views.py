# Нужна проверка авторизации, добавлять/удалять/менять магазин может только админ

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import Store
from backend.serializers.store_serializers import StoreSerializer
# from backend.functions import encrypt_password


class StoresView(APIView):
    def get(self, request, *args, **kwargs):
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True)
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
                serializer = StoreSerializer(data=request.data.copy())
                if serializer.is_valid():
                    serializer.save()
                    return Response(f'Store {serializer.validated_data["name"]} created successfully',
                                    status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        oldname = request.data.get('name', None)
        newname = request.data.get('newname', None)
        delivery_cost = request.data.get('delivery_cost', None)
        mutable_request = request.data.copy()
        if newname is not None:
            mutable_request['name'] = newname
        del mutable_request['newname']
        if delivery_cost is not None:
            mutable_request['delivery_cost'] = delivery_cost
        store = Store.objects.get(name=oldname)
        serializer = StoreSerializer(store, data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            return Response(f'Store {serializer.validated_data["name"]} updated successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        storename = request.data.get('name', None)
        store = Store.objects.get(name=storename)
        store.delete()
        return Response(f'Store {storename} deleted successfully',
                        status=status.HTTP_201_CREATED)