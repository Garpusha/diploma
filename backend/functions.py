from hashlib import md5

def encrypt_password(password):
    return md5(password.encode('utf-8')).hexdigest()