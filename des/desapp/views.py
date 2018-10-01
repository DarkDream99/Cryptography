from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from cryptodes.des import encrypt as des_encrypt
from cryptodes.des import _convert_to_string
from bitarray import bitarray


def index(request):
    context = {}
    return render(request, 'desapp/index.html', context)


def encrypt(request, *argv):
    try:
        text = request.GET['text']
        key = request.GET['key']

        bits = des_encrypt(text, key)
        return JsonResponse([bits.tobytes().decode('utf-8', 'replace'), _convert_to_string(bits)], safe=False)
    except:
        context = {
            'args': argv
        }
        return render(request, 'desapp/encrypt.html', context)
