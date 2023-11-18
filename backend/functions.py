import os
import random
import smtplib
import string
from email.header import Header
from email.mime.text import MIMEText
from hashlib import md5

import yaml
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from backend.models import User, Store, OrderProduct, ProductStore


def total_items_cost(queryset):
    required_data = list(OrderProduct.objects.filter(order=queryset.id).values())
    total_cost = 0
    # Считаю общую стоимость товаров, входящих в заказ
    for product in required_data:
        total_cost += product["price"] * product["quantity"]
    return total_cost


def total_delivery_cost(queryset):
    required_data = list(OrderProduct.objects.filter(order=queryset.id).values())
    delivery_cost = 0
    stores = set()
    [stores.add(product["store_id"]) for product in required_data]
    for store in stores:
        delivery_cost += Store.objects.get(id=store).delivery_cost
    return delivery_cost


def send_email(send_to, subject, message):
    # smtp_host = 'smtp.live.com'        # microsoft
    # smtp_host = 'smtp.gmail.com'       # google
    # smtp_host = 'smtp.mail.yahoo.com'  # yahoo
    smtp_host = "smtp.yandex.ru"  # yandex
    login, password = os.environ["EMAIL_LOGIN"], os.environ["EMAIL_PASSWORD"]
    recipients_emails = [send_to]

    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = "My New Store"
    msg["To"] = send_to

    s = smtplib.SMTP(smtp_host, 587, timeout=10)
    # s.set_debuglevel(1)
    try:
        s.starttls()
        s.login(login, password)
        s.sendmail(msg["From"], recipients_emails, msg.as_string())
    finally:
        s.quit()


def generate_msg(user, order):
    msg_header = f"Dear {user.name}! \nYour order #{order.id}\n\nYou have ordered the following position(s):\n"
    msg_body = []
    order_items = OrderProduct.objects.filter(order=order)
    for count, item in enumerate(order_items):
        msg_body.append(
            f"{count + 1}. {item.product.name} x {item.quantity} pcs x {item.price} = {item.price * item.quantity} from store {item.store.name}"
        )
    msg_basement = f"\n\nTotal cost is {total_items_cost(order)}, delivery cost is {total_delivery_cost(order)}\n\nThank you!\n"
    msg = msg_header + "\n".join(msg_body) + msg_basement
    return msg


def encrypt_password(password):
    return md5(password.encode("utf-8")).hexdigest()


def generate_token():
    source_string = string.ascii_letters + string.digits + string.punctuation
    random_string = "".join(random.choice(source_string) for i in range(20))
    token = encrypt_password(random_string)
    return token


def read_yaml(filename):
    # fs = FileSystemStorage()
    # filename = fs.save(filename.name, filename)
    # basedir = str(settings.BASE_DIR)
    # uploaded_file = (basedir + fs.url(filename))
    with open(filename) as yaml_file:
        loaded_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    # fs.delete(uploaded_file)
    return loaded_data


def import_data(data_to_import, import_serializer):
    for position in data_to_import:
        for key, value in position.items():
            serializer = import_serializer(data=value)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
    return "ok"


def is_token_exists(request):
    token = request.headers["Authorization"][6:]
    try:
        user = User.objects.get(token=token)
    except ObjectDoesNotExist:
        return False
    return user


def is_role(request, roles):
    token = request.headers["Authorization"][6:]
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


def is_store_owner(request, store_id):
    token = request.headers["Authorization"][6:]
    user = User.objects.get(token=token)
    store_owner = Store.objects.get(id=store_id).owner
    if user == store_owner:
        return True
    return False


def get_object_by_name(name, instance):
    try:
        result = instance.objects.get(name=name)
    except ObjectDoesNotExist:
        return False
    return result


def get_user_by_token(request):
    token = request.headers["Authorization"][6:]
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
        items_in_store = ProductStore.objects.get(
            store=store, product=item.product
        ).quantity
        if item.quantity > items_in_store:
            not_enough = True
            response.append(
                f"In store {store.name} only {items_in_store} pcs of product {item.product}. {item.quantity} required\n"
            )
    if not_enough:
        return response
    return False


def delete_from_store(order):
    products = OrderProduct.objects.filter(order=order)
    for item in products:
        items_in_store = ProductStore.objects.get(
            store=item.store, product=item.product
        )
        items_in_store.quantity -= item.quantity
        items_in_store.save()
