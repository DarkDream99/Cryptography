from django.shortcuts import render
from django.http import JsonResponse
from .libs.cryptorsa import cryptorsa
import os
import pickle


VIEW_POSITION = os.path.dirname(os.path.realpath(__file__))
KEYS = set()
CRYPT_TEXT = b""
SOURCE_TEXT = ""
SERVER_URL = ""


def index(request):
    context = {}
    return render(request, 'rsapp/index.html', context)


def public_keys(request, *args):
    path_to_pub = os.path.join(VIEW_POSITION, 'files', 'obj', 'pub_client.key')
    hpub_client = open(path_to_pub, 'rb')
    pub_client = pickle.load(hpub_client)
    return JsonResponse({'e': pub_client.e, 'n': pub_client.n}, safe=False)


def server_key(request, *args):
    if request.POST:
        e = request.POST['e']
        n = request.POST['n']

        pub_key = cryptorsa.create_public_key(e, n)
        path_to_pub_server = os.path.join(VIEW_POSITION, 'files', 'obj', 'pub_server.key')
        hpub_server = open(path_to_pub_server, 'wb')
        pickle.dump(pub_key, hpub_server)

        return JsonResponse(pub_key, safe=True)


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
            'public': pub_key.e,
            'private': priv_key.d
        }

        return render(request, 'rsapp/create_keys.html', context)
    else:
        hpub_client = open(request.session['pub_client_key'], 'rb')
        pub_client = pickle.load(hpub_client)
        hpriv_client = open(request.session['priv_client_key'], 'rb')
        priv_client = pickle.load(hpriv_client)

        context = {
            'public': pub_client.e,
            'private': priv_client.d
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
            'crypted_text': CRYPT_TEXT.decode("utf-8", "replace"),
        }
        return render(request, 'rsapp/crypt_text.html', context)
    else:
        message = request.GET['message']
        SOURCE_TEXT = message

    path_to_pub_client = os.path.join(VIEW_POSITION, 'files', 'obj', 'pub_client.key')
    hpub_client = open(path_to_pub_client, 'rb')
    pub_client = pickle.load(hpub_client)

    CRYPT_TEXT = cryptorsa.crypt(pub_client, message)

    return JsonResponse([CRYPT_TEXT.decode("utf-8", "replace")], safe=False)


def decrypt(request, *args):
    global CRYPT_TEXT
    if not CRYPT_TEXT:
        context = {}
        return render(request, 'rsapp/decrypt_bits.html', context)

    path_to_priv_client = os.path.join(VIEW_POSITION, 'files', 'obj', 'priv_client.key')
    hpriv_client = open(path_to_priv_client, 'rb')
    priv_client = pickle.load(hpriv_client)

    decrypt_text = cryptorsa.decrypt(priv_client, CRYPT_TEXT)

    return JsonResponse([decrypt_text], safe=False)
