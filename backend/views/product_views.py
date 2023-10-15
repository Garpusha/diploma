# Нужна проверка авторизации, добавлять/удалять/менять товар может только продавец

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import Product, Category
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
                mutable_request = request.data.copy()
                category = mutable_request.get('category', None)
                category_id = Category.objects.get(name=category).id
                if category_id is None:
                    return Response('Wrong category', status=status.HTTP_400_BAD_REQUEST)
                mutable_request['category'] = category_id
                # del mutable_request['category']
                serializer = ProductSerializer(data=mutable_request)
                if serializer.is_valid():
                    serializer.save()
                    return Response(f'Product {serializer.validated_data["name"]} created successfully',
                                    status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)



    def patch(self, request, *args, **kwargs):
        product_id = request.data.get('id', None)
        mutable_request = request.data.copy()
        product = Product.objects.get(id=product_id)
        category = mutable_request.get('category', None)
        category_id = Category.objects.get(name=category).id
        if category_id is None:
            return Response('Wrong category', status=status.HTTP_400_BAD_REQUEST)
        mutable_request['category_id'] = category_id
        del mutable_request['category']
        serializer = ProductSerializer(product, data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            return Response(f'Product {serializer.validated_data["name"]} updated successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('id', None)
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response(f'Product deleted successfully',
                        status=status.HTTP_201_CREATED)