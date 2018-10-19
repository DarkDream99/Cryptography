from django.shortcuts import render
from django.http import JsonResponse
from .libs.cryptorsa import cryptorsa
import os
import pickle


VIEW_POSITION = os.path.dirname(os.path.realpath(__file__))
KEYS = set()
CRYPT_TEXT = b""
SOURCE_TEXT = ""
SERVER_CRYPT_TEXT = ""
SERVER_URL = ""


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


def change_key(request, *args):
    path_to_pub = os.path.join(VIEW_POSITION, 'files', 'obj', 'pub_client.key')
    path_to_priv = os.path.join(VIEW_POSITION, 'files', 'obj', 'priv_client.key')

    pub_key, priv_key = cryptorsa.create_keys()

    hpub_client = open(path_to_pub, 'wb')
    pickle.dump(pub_key, hpub_client)

    hpriv_client = open(path_to_priv, 'wb')
    pickle.dump(priv_key, hpriv_client)

    return JsonResponse([repr(pub_key), repr(priv_key)], safe=False)


def create_keys(request, *args):
    path_to_pub = os.path.join(VIEW_POSITION, 'files', 'obj', 'pub_client.key')
    path_to_priv = os.path.join(VIEW_POSITION, 'files', 'obj', 'priv_client.key')

    if 'priv_client_key' not in KEYS:
        pub_key, priv_key = cryptorsa.create_keys()

        hpub_client = open(path_to_pub, 'wb')
        pickle.dump(pub_key, hpub_client)

        hpriv_client = open(path_to_priv, 'wb')
        pickle.dump(priv_key, hpriv_client)

        request.session['pub_client_key'] = path_to_pub
        request.session['priv_client_key'] = path_to_priv

        KEYS.add('priv_client_key')
        KEYS.add('pub_client_key')

        hpub_client.close()
        hpriv_client.close()

        context = {
            'public': pub_key,
            'private': priv_key
        }

        return render(request, 'rsapp/create_keys.html', context)
    else:
        hpub_client = open(request.session['pub_client_key'], 'rb')
        pub_client = pickle.load(hpub_client)
        hpriv_client = open(request.session['priv_client_key'], 'rb')
        priv_client = pickle.load(hpriv_client)

        context = {
            'public': pub_client,
            'private': priv_client
        }
        return render(request, 'rsapp/create_keys.html', context)


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
    global CRYPT_TEXT
    global SOURCE_TEXT

    if 'message' not in request.GET:
        context = {
            'source_text': SOURCE_TEXT,
            'crypted_text': list(CRYPT_TEXT),
        }
        return render(request, 'rsapp/crypt_text.html', context)
    else:
        message = request.GET['message']
        SOURCE_TEXT = message

    path_to_pub_server = os.path.join(VIEW_POSITION, 'files', 'obj', 'pub_server.key')
    hpub_server = open(path_to_pub_server, 'rb')
    pub_server = pickle.load(hpub_server)

    CRYPT_TEXT = cryptorsa.crypt(pub_server, message)

    bytes_code_text = [(x - 128) for x in list(CRYPT_TEXT)]
    return JsonResponse([bytes_code_text], safe=False)


def decrypt(request, *args):
    global SERVER_CRYPT_TEXT
    if not SERVER_CRYPT_TEXT:
        context = {}
        return render(request, 'rsapp/decrypt_bits.html', context)

    path_to_priv_client = os.path.join(VIEW_POSITION, 'files', 'obj', 'priv_client.key')
    hpriv_client = open(path_to_priv_client, 'rb')
    priv_client = pickle.load(hpriv_client)

    decrypt_text = cryptorsa.decrypt(priv_client, SERVER_CRYPT_TEXT)

    return JsonResponse([decrypt_text], safe=False)


def send_text(request, *args):
    context = {
        SERVER_URL
    }

    return render(request, "rsapp/send_text.html", context)

