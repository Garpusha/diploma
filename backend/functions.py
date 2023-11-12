from hashlib import md5
import yaml
import random, string

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from backend.models import User, Store, OrderProduct, ProductStore


def encrypt_password(password):
    return md5(password.encode('utf-8')).hexdigest()


def generate_token():
    source_string = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choice(source_string) for i in range(20))
    token = encrypt_password(random_string)
    return token


def read_yaml(filename):
    fs = FileSystemStorage()
    filename = fs.save(filename.name, filename)
    basedir = str(settings.BASE_DIR)
    uploaded_file = (basedir + fs.url(filename))
    with open(uploaded_file) as yaml_file:
        loaded_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    fs.delete(uploaded_file)
    return loaded_data


def import_data(data_to_import, import_serializer):
    for position in data_to_import:
        for key, value in position.items():
            serializer = import_serializer(data=value)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
    return 'ok'


def is_token_exists(request):
    token = request.headers['Authorization'][6:]
    try:
        User.objects.get(token=token)
    except ObjectDoesNotExist:
        return False
    return True


def is_role(request, roles):
    token = request.headers['Authorization'][6:]
    user = User.objects.get(token=token)
    if user.role in roles:
        return True
    return False


def is_exists(item, instance):
    try:
        result = instance.objects.get(id=item)
    except ObjectDoesNotExist:
        return False
    return result


def is_store_owner(request):
    token = request.headers['Authorization'][6:]
    user = User.objects.get(token=token)
    store_owner = Store.objects.get(id=request.data['store']).owner
    if user == store_owner:
        return True
    return False


def get_id_by_name(name, instance):
    try:
        result = instance.objects.get(name=name).id
    except ObjectDoesNotExist:
        return False
    return result


def get_user_by_token(request):
    token = request.headers['Authorization'][6:]
    user = User.objects.get(token=token)
    return user


# Функция проверяет наличие товаров в магазинах перед оформлением заказа. Если всего хватает, возвращает False,
# если нет, сообщение о нехватке.
def check_balance(order):
    products = OrderProduct.objects.filter(order=order)
    response = []
    not_enough = False
    for item in products:
        store = item.store
        items_in_store = ProductStore.objects.get(store=store, product=item.product).quantity
        if item.quantity > items_in_store:
            not_enough = True
            response.append(f'In store {store.name} only {items_in_store} pcs of product {item.product}. {item.quantity} required\n')
    if not_enough:
        return response
    return False


def delete_from_store(order):
    products = OrderProduct.objects.filter(order=order)
    for item in products:
        items_in_store = ProductStore.objects.get(store=item.store, product=item.product)
        items_in_store.quantity -= item.quantity
        items_in_store.save()


def notify_by_email(order):
    pass
