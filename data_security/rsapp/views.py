import os
import json
import requests
import pickle
from datetime import datetime
from functools import wraps

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import User as UserModel
from base64 import b64encode

from .libs.cryptorsa import cryptorsa


VIEW_POSITION = os.path.dirname(os.path.realpath(__file__))
SERVER_API_URL = ""


class RSAKey:
    def __init__(self, public=None, private=None):
        self.public = public
        self.private = private


class Key(object):
    def __init__(self, rsa_key: RSAKey=None, date=None):
        self.rsa_key = rsa_key
        self.date = date


SERVER_RSA_KEY: Key = None
SERVER_DES_KEY = 1215516513


class User(object):
    def __init__(self, name=None, crypt_key: Key=None):
        self.name = name
        self.key = crypt_key

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name is other.name


USERS = {}


def _create_user(user_name: str, key: Key=None) -> User:
    key = _create_key() if not key else key
    user = User(name=user_name, crypt_key=key)
    return user


def _load_users():
    global USERS
    user_objects = UserModel.objects.all()

    for user in user_objects:
        name = user.name
        key = pickle.loads(user.key)
        USERS[name] = _create_user(name, key)


_load_users()


def index(request):
    context = {}
    return render(request, 'rsapp/index.html', context)


def _create_key() -> Key:
    pub_key, priv_key = cryptorsa.create_keys()
    key = Key(
        rsa_key=RSAKey(pub_key, priv_key),
        date=datetime.now()
    )

    return key


def get_requested(template_url):
    def get_request(source_func):
        @wraps(source_func)
        def wrapper(request, *args, **kwargs):
            if request.method == "GET":
                return source_func(request, *args, **kwargs)
            return render(request, template_url)

        return wrapper

    return get_request


def get_filled(*fields):
    def get_fill(source_func):
        @wraps(source_func)
        def wrapper(request, *args, **kwargs):
            for field in fields:
                if field not in request.GET or not request.GET[field]:
                    return None

            return source_func(request, *args, **kwargs)

        return wrapper

    return get_fill


def post_filled(*fields):
    def post_fill(source_func):
        @wraps(source_func)
        def wrapper(request, *args, **kwargs):
            for field in fields:
                if field not in request.POST or not request.POST[field]:
                    return None

            return source_func(request, *args, **kwargs)

        return wrapper

    return post_fill


def rsa_key_refreshed(user_name: str):
    global USERS

    user = USERS[user_name]
    key = user.key
    curr_date = datetime.now()

    date_delta = curr_date - key.date
    if date_delta.seconds > 30:
        USERS[user_name].key = _create_key()
        user_obj = UserModel.objects.filter(name=user_name)[0]
        user_obj.key = pickle.dumps(USERS[user_name].key)
        user_obj.save()


@get_filled("user_name")
def _create_keys_get(request, *args):
    global USERS

    user_name = request.GET["user_name"]
    if user_name in USERS:
        rsa_key_refreshed(user_name)
        data = {
            "public": repr(USERS[user_name].key.rsa_key.public),
            "private": repr(USERS[user_name].key.rsa_key.private)
        }
        return JsonResponse(data, safe=False)

    return HttpResponse("Unauthorized", status=401)


@post_filled("user_name")
def _create_keys_post(request, *args):
    global USERS

    user_name = request.POST["user_name"]
    USERS[user_name] = _create_user(user_name)

    user_objs = UserModel.objects.filter(name=user_name)
    if user_objs:
        user_objs[0].key = pickle.dumps(USERS[user_name].key)
        user_objs[0].save()
    else:
        user_obj = UserModel.objects.create(
            name=user_name,
            key=pickle.dumps(USERS[user_name].key))
        user_obj.save()


def create_keys(request, *args):
    if request.method == "GET":
        response = _create_keys_get(request, *args)
        if not response:
            return render(request, "rsapp/create_keys.html")
        return response

    _create_keys_post(request, *args)
    return render(request, "rsapp/create_keys.html")


def crypt(request, *args):
    global USERS

    if request.method == "GET":
        if "message" not in request.GET:
            return render(request, "rsapp/crypt_text.html")

        user_name = request.GET["user_name"]
        if user_name not in USERS:
            return HttpResponse("Unauthorized", status=401)

        rsa_key_refreshed(user_name)
        if "message" in request.GET and request.GET["message"]:
            message = request.GET["message"]
            user_key = USERS[user_name].key
            crypt_bytes = cryptorsa.crypt(user_key.rsa_key.public, message)
            crypt_bytes = list(crypt_bytes)
            return JsonResponse(crypt_bytes, safe=False)

        return HttpResponse("The message field must be entered!", status=400)


def decrypt(request, *args):
    global USERS

    if request.method == "GET":
        if "user_name" not in request.GET:
            return render(request, "rsapp/decrypt_bits.html")

        if "crypt_bytes" in request.GET and request.GET["crypt_bytes"]:
            user_name = request.GET["user_name"]
            json_bytes = json.loads(request.GET["crypt_bytes"])
            crypt_bytes = bytes(json_bytes)

            if user_name not in USERS:
                return HttpResponse("Unauthorized", status=401)

            user_key = USERS[user_name].key
            decrypt_text = cryptorsa.decrypt(user_key.rsa_key.private, crypt_bytes)
            return JsonResponse(decrypt_text, safe=False)

    return HttpResponse("The user_name and crypt_bytes fields must be entered!", status=400)


def _encrypt_xor(message: str, key: int) -> list:
    res_bytes = list(bytes(b64encode(message.encode("utf-8"))))
    res_bytes = [x ^ key for x in res_bytes]
    return res_bytes


def send_text(request, *args):
    global SERVER_API_URL
    global USERS
    global SERVER_DES_KEY

    if request.method == "GET":
        context = {
            "server_url": SERVER_API_URL
        }
        return render(request, "rsapp/send_text.html", context)

    if "user_name" in request.POST:
        user_name = request.POST["user_name"]
        if "server_url" in request.POST:
            SERVER_API_URL = request.POST["server_url"]
            if "crypt_bytes" in request.POST:
                crypt_bytes = [int(x) for x in request.POST["crypt_bytes"].split(',')]
                crypt_bytes = bytes(crypt_bytes)

                if user_name in USERS:
                    user_key = USERS[user_name].key
                    decrypt_text = cryptorsa.decrypt(user_key.rsa_key.private, crypt_bytes)
                    decrypt_text = "\n--Written by " + user_name + "--\n" + decrypt_text

                    encrypt_des = _encrypt_xor(decrypt_text, SERVER_DES_KEY)
                    requests.post(SERVER_API_URL, json=encrypt_des)

    context = {
        "server_url": SERVER_API_URL
    }
    return render(request, "rsapp/send_text.html", context)
