from django.db import models


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


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)


class Store(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)
    delivery_cost = models.DecimalField(max_digits=11, decimal_places=2, blank=False)


class Product(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)


class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, blank=False)


class Position(models.Model):
    store_id = models.ForeignKey(Store, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(blank=False)


class ProductStore(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    store_id = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(blank=False)
    price = models.DecimalField(max_digits=11, decimal_places=2, blank=False)


class OrderPosition(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    position_id = models.ForeignKey(Position, on_delete=models.CASCADE)


class Parameters(models.Model):
    name = models.CharField(max_length=20, unique=False, blank=False)
    value = models.CharField(max_length=50, unique=False, blank=False)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)

