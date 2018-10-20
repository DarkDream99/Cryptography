import os
import pickle
from datetime import datetime
import json
import requests

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from Crypto.Cipher import DES
from base64 import b64encode

from .libs.cryptorsa import cryptorsa


VIEW_POSITION = os.path.dirname(os.path.realpath(__file__))
KEYS = set()
CRYPT_TEXT = b""
SOURCE_TEXT = ""
SERVER_CRYPT_TEXT = ""
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
SERVER_DES_KEY = 121551651316848151456313494561346549


class User(object):
    def __init__(self, name=None, crypt_key: Key=None):
        self.name = name
        self.key = crypt_key

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name is other.name


USERS = {}


def index(request):
    context = {}
    return render(request, 'rsapp/index.html', context)


def public_keys(request, *args):
    path_to_pub = os.path.join(VIEW_POSITION, 'files', 'obj', 'pub_client.key')
    hpub_client = open(path_to_pub, 'rb')
    pub_client = pickle.load(hpub_client)
    return JsonResponse({'e': str(pub_client.e), 'n': str(pub_client.n)}, safe=False)


def server_key(request, *args):
    if request.GET:
        e = int(request.GET['e'].replace("\"", ""))
        n = int(request.GET['n'].replace("\"", ""))

        pub_key = cryptorsa.create_public_key(e, n)
        path_to_pub_server = os.path.join(VIEW_POSITION, 'files', 'obj', 'pub_server.key')
        hpub_server = open(path_to_pub_server, 'wb')
        pickle.dump(pub_key, hpub_server)

        return JsonResponse(repr(pub_key), safe=False)


def _create_key() -> Key:
    pub_key, priv_key = cryptorsa.create_keys()
    key = Key(
        rsa_key=RSAKey(pub_key, priv_key),
        date=datetime.now()
    )

    return key


def create_keys(request, *args):
    global USERS
    if request.method == "GET":
        if "user_name" in request.GET:
            user_name = request.GET["user_name"]
            if user_name in USERS:
                data = {
                    "public": repr(USERS[user_name].key.rsa_key.public),
                    "private": repr(USERS[user_name].key.rsa_key.private)
                }

                return JsonResponse(data, safe=False)

    if "user_name" in request.POST:
        user_name = request.POST["user_name"]
        key = _create_key()
        user = User(name=user_name, crypt_key=key)
        USERS[user_name] = user

    return render(request, "rsapp/create_keys.html")


def change_server_url(request, *args):
    global SERVER_API_URL
    SERVER_API_URL = request.GET["server_url"]


def gener_swap_keys(request, *args):
    global SERVER_API_URL
    global SERVER_DES_KEY

    if request.method == "GET":
        context = {
            "server_url": SERVER_API_URL
        }
        return render(request, "rsapp/swap_keys.html")

    if "server_url" in request.POST:
        SERVER_API_URL = request.POST["server_url"]
        req_data = {"des_key": SERVER_DES_KEY}
        requests.post(SERVER_API_URL, json=req_data)


def crypt(request, *args):
    global USERS

    if request.method == "GET":
        if "message" not in request.GET:
            return render(request, "rsapp/crypt_text.html")

        user_name = request.GET["user_name"]
        if user_name not in USERS:
            return HttpResponse("Unauthorized", status=401)

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


def _pad(s):
    return s + (DES.block_size - len(s) % DES.block_size) * \
        chr(DES.block_size - len(s) % DES.block_size)


def _encrypt_des(message: str, key: str) -> bytes:
    des_gener = DES.new(key, DES.MODE_CTR)
    return b64encode(des_gener.encrypt(_pad(message)))


def _encrypt_xor(message: str, key: int) -> list:
    res_bytes = list(bytes(message.encode("utf-8")))
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
                    decrypt_text += "\n--Written by " + user_name + "--\n"

                    encrypt_des = _encrypt_xor(decrypt_text, SERVER_DES_KEY)
                    response_data = {
                        "des_message": encrypt_des
                    }
                    requests.post(SERVER_API_URL, json=response_data)

    context = {
        "server_url": SERVER_API_URL
    }
    return render(request, "rsapp/send_text.html", context)
