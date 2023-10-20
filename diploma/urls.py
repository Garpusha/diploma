"""diploma URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from backend.views.order_views import OrderView
# from backend.functions import list_users
from backend.views.user_views import UsersView
from backend.views.store_views import StoresView
from backend.views.product_views import ProductsView
from backend.views.category_views import CategoriesView
from backend.views.parameters_views import ParametersView
from backend.views.product_store_views import ProductStoreView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', UsersView.as_view()),
    path('stores/', StoresView.as_view()),
    path('products/', ProductsView.as_view()),
    path('categories/', CategoriesView.as_view()),
    path('parameters/', ParametersView.as_view()),
    path('product_in_store/', ProductStoreView.as_view()),
    path('orders/', OrderView.as_view()),

    # path('list_users/', list_users),
]
