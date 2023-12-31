from django.db import models


# Учетка пользователя
class User(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)
    password = models.CharField(max_length=32, blank=False)
    role = models.CharField(max_length=10, blank=False)
    email = models.CharField(max_length=50, unique=True, blank=False)
    address_1 = models.CharField(max_length=100, blank=True)
    address_2 = models.CharField(max_length=100, blank=True)
    address_3 = models.CharField(max_length=100, blank=True)
    address_4 = models.CharField(max_length=100, blank=True)
    address_5 = models.CharField(max_length=100, blank=True)
    token = models.CharField(max_length=32, blank=True)
    temp_token = models.CharField(max_length=32, blank=True)


# Категория товара (телефоны, планшеты и т.п.)
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)


# Магазин
class Store(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    delivery_cost = models.DecimalField(max_digits=11, decimal_places=2, blank=False)
    active = models.BooleanField(blank=False, default=True)


# Товар
class Product(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True)
    description = models.TextField(blank=False)

    def __str__(self):
        return self.name


# Заказ одного пользователя
class Order(models.Model):
    status = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


# Корзина товаров одного пользователя
class OrderProduct(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=11, decimal_places=2, default=0)


# Количество и цена одного товара в одном магазине
class ProductStore(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(blank=False)
    price = models.DecimalField(max_digits=11, decimal_places=2, blank=False)


# Параметр товара (размер, вес, количество памяти и т.п.)
class Parameter(models.Model):
    name = models.CharField(max_length=40, unique=True, blank=False)


class ProductParameter(models.Model):
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE)
    value = models.CharField(max_length=50, unique=False, blank=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="parameters"
    )
