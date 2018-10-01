from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def index(request):
    context = {}
    return render(request, 'desapp/index.html', context)


def encrypt(request, *argv):
    context = {
        'args': argv
    }
    return render(request, 'desapp/encrypt.html', context)
