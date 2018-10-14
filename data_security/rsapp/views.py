from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'rsapp/index.html', context)


def create_keys(request, *argv):
    context = {}
    return render(request, 'rsapp/create_keys.html', context)
