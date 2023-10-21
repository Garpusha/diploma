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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True)
    description = models.TextField(blank=False)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, blank=True)
    # total_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderProduct(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(blank=False)
    price = models.DecimalField(max_digits=11, decimal_places=2, blank=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)


class ProductStore(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(blank=False)
    price = models.DecimalField(max_digits=11, decimal_places=2, blank=False)


class Parameter(models.Model):
    name = models.CharField(max_length=20, unique=False, blank=False)
    value = models.CharField(max_length=50, unique=False, blank=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
