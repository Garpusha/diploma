from hashlib import md5
import yaml
import random, string

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from backend.models import User


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


def is_token_exists(token):
    try:
        User.objects.get(token=token)
    except ObjectDoesNotExist:
        return False
    return True


def is_admin(request):
    token = request.headers['Authorization'][6:]
    if not is_token_exists(token):
        return Response('Wrong token', status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(token=token)
    if user.role != 'admin':
        return Response('Admin rights required', status=status.HTTP_400_BAD_REQUEST)
    return 'ok'

def is_seller(request):
    token = request.headers['Authorization'][6:]
    if not is_token_exists(token):
        return Response('Wrong token', status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(token=token)
    if user.role != 'seller':
        return Response('Owner should have seller role', status=status.HTTP_400_BAD_REQUEST)
    return 'ok'

def is_seller_or_admin(request):
    token = request.headers['Authorization'][6:]
    if not is_token_exists(token):
        return Response('Wrong token', status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(token=token)
    if user.role == 'seller' or user.role == 'admin':
        return 'ok'
    return Response('Admin or seller rights required', status=status.HTTP_400_BAD_REQUEST)

# def list_users(request):
#     users = list(User.objects.values())
#     context = {'my_context': users}
#     return render(request, 'users.html', context)
#
