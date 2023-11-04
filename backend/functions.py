from hashlib import md5
import yaml
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response


# from backend.models import User
# from django.shortcuts import render


def encrypt_password(password):
    return md5(password.encode('utf-8')).hexdigest()


def read_yaml(filename):
    fs = FileSystemStorage()
    filename = fs.save(filename.name, filename)
    basedir = str(settings.BASE_DIR)
    uploaded_file = basedir + fs.url(filename)
    with open(uploaded_file) as yaml_file:
        loaded_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    return loaded_data


def import_data(data_to_import, import_serializer):
    for position in data_to_import:
        for key, value in position.items():
            serializer = import_serializer(data=value)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
    return 'ok'

# def list_users(request):
#     users = list(User.objects.values())
#     context = {'my_context': users}
#     return render(request, 'users.html', context)
#
