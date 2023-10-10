# Нужна проверка авторизации, добавлять/удалять/менять товар может только продавец

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import Product
from backend.serializers.product_serializers import ProductSerializer
# from backend.functions import encrypt_password

class ProductsView(APIView):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
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
                serializer = ProductSerializer(data=request)
                if serializer.is_valid():
                    serializer.save()
                    return Response(f'Product {serializer.validated_data["name"]} created successfully',
                                    status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)



    def patch(self, request, *args, **kwargs):
        productname = request.data.get('name', None)
        product = Store.objects.get(name=productname)
        serializer = ProductSerializer(product, data=request)
        if serializer.is_valid():
            serializer.save()
            return Response(f'Product {serializer.validated_data["name"]} updated successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        productname = request.data.get('name', None)
        product = Store.objects.get(name=productname)
        product.delete()
        return Response(f'Store {productname} deleted successfully',
                        status=status.HTTP_201_CREATED)