from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def index(request):
    template = loader.get_template('desapp/index.html')
    context = {}
    # return HttpResponse(template.render(context, request))
    return render(request, 'desapp/index.html', context)
