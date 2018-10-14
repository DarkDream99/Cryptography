from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'rsapp/index.html', context)


def create_keys(request, *args):
    context = {}
    return render(request, 'rsapp/create_keys.html', context)


def swap_keys(request, client_key=None, *args):
    context = {}
    return render(request, 'rsapp/swap_keys.html', context)


def change_text(request, bits=None, *args):
    context = {}
    return render(request, 'rsapp/send_text.html', context)


def crypt(request, message=None, *args):
    context = {}
    return render(request, 'rsapp/crypt_text.html', context)


def decrypt(request, bits=None, *args):
    context={}
    return render(request, 'rsapp/decrypt_bits.html', context)
