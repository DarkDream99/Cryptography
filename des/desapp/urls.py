from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path('encrypt(\\.html)?/<text>/<key>', views.encrypt),
    re_path('encrypt(\\.html)?/', views.encrypt),
    path('', views.index, name='DES'),
]