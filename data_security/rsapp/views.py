import os
import pickle
from datetime import datetime
import json

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from .libs.cryptorsa import cryptorsa


VIEW_POSITION = os.path.dirname(os.path.realpath(__file__))
KEYS = set()
CRYPT_TEXT = b""
SOURCE_TEXT = ""
SERVER_CRYPT_TEXT = ""
SERVER_URL = ""


class RSAKey:
    def __init__(self, public=None, private=None):
        self.public = public
        self.private = private


class Key(object):
    def __init__(self, rsa_key: RSAKey=None, date=None):
        self.rsa_key = rsa_key
        self.date = date


SERVER_RSA_KEY: Key = None


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
    global SERVER_URL
    SERVER_URL = request.GET["server_url"]


def gener_swap_keys(request, *args):
    path_to_pub_server = os.path.join(VIEW_POSITION, 'files', 'obj', 'pub_server.key')
    path_to_priv_server = os.path.join(VIEW_POSITION, 'files', 'obj', 'priv_server.key')

    if 'pub_server_key' not in KEYS:
        pub_key, priv_key = cryptorsa.create_keys()

        hpub_server = open(path_to_pub_server, 'wb')
        hpriv_server = open(path_to_priv_server, 'wb')

        pickle.dump(pub_key, hpub_server)
        pickle.dump(priv_key, hpriv_server)

        request.session['pub_server_key'] = path_to_pub_server
        request.session['priv_server_key'] = path_to_priv_server

        hpub_server.close()
        hpriv_server.close()

    if 'pub_client_key' in KEYS:
        hpub_client = open(request.session['pub_client_key'], 'rb')
        pub_client = pickle.load(hpub_client)
        hpub_server = open(request.session['pub_server_key'], 'rb')
        pub_server = pickle.load(hpub_server)

        context = {
            'server_url': SERVER_URL,
            'pub_client_key': pub_client,
            'pub_server_key': pub_server
        }
        return render(request, 'rsapp/swap_keys.html', context)

    context = {
        'server_url': SERVER_URL,
    }
    return render(request, 'rsapp/swap_keys.html', context)


def change_text(request, bits=None, *args):
    context = {
        'server_url': SERVER_URL,
    }
    return render(request, 'rsapp/send_text.html', context)


def crypt(request, *args):
    global SERVER_RSA_KEY
    if not SERVER_RSA_KEY:
        SERVER_RSA_KEY = _create_key()

    if request.method == "GET":
        if "message" not in request.GET:
            return render(request, "rsapp/crypt_text.html")

        if "message" in request.GET and request.GET["message"]:
            message = request.GET["message"]
            crypt_bytes = cryptorsa.crypt(SERVER_RSA_KEY.rsa_key.public, message)
            crypt_bytes = list(crypt_bytes)
            return JsonResponse(crypt_bytes, safe=False)

        return HttpResponse("The message field must be entered!", status=400)


def decrypt(request, *args):
    if request.method == "GET":
        if "user_name" not in request.GET:
            return render(request, "rsapp/crypt_text.html")

        if "crypt_bytes" in request.GET and request.GET["crypt_bytes"]:
            user_name = request.GET["user_name"]
            crypt_bytes = bytes(json.load(request.GET["crypt_bytes"]))

            if user_name not in USERS:
                return HttpResponse("Unauthorized", status=401)

            user_key = USERS[user_name]
            decrypt_text = cryptorsa.decrypt(user_key.rsa_key.private, crypt_bytes)
            return JsonResponse(decrypt_text, safe=False)

    return HttpResponse("The user_name and crypt_bytes fields must be entered!", status=400)


def send_text(request, *args):
    context = {
        SERVER_URL
    }

    return render(request, "rsapp/send_text.html", context)

