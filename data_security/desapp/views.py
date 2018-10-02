from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# from cryptodes.des import encrypt as des_encrypt
# from cryptodes.des import decrypt as des_decrypt
# from cryptodes.des import _convert_to_string
from .libs.cryptodes.des import encrypt as des_encrypt
from .libs.cryptodes.des import decrypt as des_decrypt
from .libs.cryptodes.des import convert_to_string
from bitarray import bitarray


def index(request):
    context = {}
    return render(request, 'desapp/index.html', context)


def encrypt(request, *args):
    try:
        text = request.GET['text']
        key = request.GET['key']

        bits, entropies = des_encrypt(text, key)
        return JsonResponse([bits.tobytes().decode('utf-8', 'replace'), convert_to_string(bits), entropies], safe=False)
    except:
        context = {
            'args': args
        }
        return render(request, 'desapp/encrypt.html', context)


def convert_to_bits(request, *args):
    text = request.GET['text']
    res_bits = bitarray()
    res_bits.fromstring(text)
    return HttpResponse(convert_to_string(res_bits))


def decrypt(request, *args):
    try:
        code = request.GET['code']
        key = request.GET['key']

        bits_code = bitarray()
        for bit in code:
            bits_code.append(1 if bit == '1' else 0)

        bits_decode = des_decrypt(bits_code, key)
        return JsonResponse([bits_decode.tobytes().decode('utf-8', 'replace'), convert_to_string(bits_decode)],
                            safe=False)
    except:
        context = {}
        return render(request, 'desapp/decrypt.html', context)


def convert_to_text(request, *args):
    bits = request.GET['bits']
    bits_code = bitarray()
    for bit in bits:
        bits_code.append(1 if bit == '1' else 0)

    return HttpResponse(bits_code.tobytes().decode("utf-8", "replace"))
