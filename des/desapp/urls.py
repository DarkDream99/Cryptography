from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path('encrypt(\.html)?/bits/', views.convert_to_bits),
    re_path('encrypt(\.html)?/', views.encrypt),
    re_path('decrypt(.html)?/', views.decrypt),
    path('', views.index, name='DES'),
]