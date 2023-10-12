# Нужна проверка авторизации, добавлять/удалять/менять категории может только админ

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models import Category
from backend.serializers.category_serializers import CategorySerializer
# from backend.functions import encrypt_password

class CategoriesView(APIView):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
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
                serializer = CategorySerializer(data=request.data.copy())
                if serializer.is_valid():
                    serializer.save()
                    return Response(f'Category {serializer.validated_data["name"]} created successfully',
                                    status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            case _:
                return Response('Wrong method', status=status.HTTP_400_BAD_REQUEST)



    def patch(self, request, *args, **kwargs):
        old_category = request.data.get('name', None)
        new_category = request.data.get('newname', None)
        category = Category.objects.get(name=old_category)
        mutable_request = request.data.copy()
        mutable_request['name'] = new_category
        del mutable_request['newname']
        serializer = CategorySerializer(category, data=mutable_request)
        if serializer.is_valid():
            serializer.save()
            return Response(f'Category {serializer.validated_data["name"]} updated successfully',
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        categoryname = request.data.get('name', None)
        category = Category.objects.get(name=categoryname)
        category.delete()
        return Response(f'Category {categoryname} deleted successfully',
                        status=status.HTTP_201_CREATED)