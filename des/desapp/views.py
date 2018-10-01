from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from cryptodes.des import encrypt as des_encrypt
from cryptodes.des import _convert_to_string
from bitarray import bitarray


def index(request):
    context = {}
    return render(request, 'desapp/index.html', context)


def encrypt(request, *args):
    try:
        text = request.GET['text']
        key = request.GET['key']

        bits = des_encrypt(text, key)
        return JsonResponse([bits.tobytes().decode('utf-8', 'replace'), _convert_to_string(bits)], safe=False)
    except:
        context = {
            'args': args
        }
        return render(request, 'desapp/encrypt.html', context)


def convert_to_bits(request, *args):
    text = request.GET['text']
    res_bits = bitarray()
    res_bits.fromstring(text)
    return HttpResponse(_convert_to_string(res_bits))


def decrypt(request, *args):
    context = {}
    return render(request, 'desapp/decrypt.html', context)
