# Нужна проверка авторизации, добавлять/удалять/менять категории может только админ

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import Parameter
from backend.serializers.parameter_serializers import ParameterSerializer
# from backend.functions import encrypt_password

class ParametersView(APIView):
    def get(self, request, *args, **kwargs):
        parameters = Parameter.objects.all().select_related('product').order_by('name')
        serializer = ParameterSerializer(parameters, many=True)
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
                serializer = ParameterSerializer(data=request.data.copy())
                if serializer.is_valid():
                    serializer.save()
                    return Response(f'Parameter created successfully',
                                    status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)



    def patch(self, request, *args, **kwargs):
        old_category = request.data.get('name', None)
        new_category = request.data.get('newname', None)
        parameter = Parameter.objects.get(name=old_category)
        mutable_request = request.data.copy()
        mutable_request['name'] = new_category
        del mutable_request['newname']
        serializer = ParameterSerializer(parameter, data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            return Response(f'Parameter updated successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        product = request.data.get('product_id', None)
        parametername = request.data.get('name', None)
        parameter = Parameter.objects.get(name=parametername, id=product)
        parameter.delete()
        return Response(f'Parameter deleted successfully',
                        status=status.HTTP_201_CREATED)