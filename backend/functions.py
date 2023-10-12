from hashlib import md5

# from backend.models import User
# from django.shortcuts import render

def encrypt_password(password):
    return md5(password.encode('utf-8')).hexdigest()


# def list_users(request):
#     users = list(User.objects.values())
#     context = {'my_context': users}
#     return render(request, 'users.html', context)
#
