from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter

# from backend.functions import list_users
from backend.views import (
    UsersView,
    ImportData,
    StoresView,
    ProductsView,
    CategoriesView,
    ParametersView,
    CartView,
    ProductStoreView,
    OrdersView,
    AuthorizationView,
)

# r = DefaultRouter()
# r.register('orders_view', OrderViewSet)
# r.register('product_in_store_view', ProductStoreViewSet)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", UsersView.as_view()),
    path("stores/", StoresView.as_view()),
    path("products/", ProductsView.as_view()),
    path("categories/", CategoriesView.as_view()),
    path("parameters/", ParametersView.as_view()),
    path("product_in_store/", ProductStoreView.as_view()),
    path("orders/", OrdersView.as_view()),
    path("import/", ImportData.as_view()),
    path("cart/", CartView.as_view()),
    path("authorization/", AuthorizationView.as_view()),
]
# + r.urls)
