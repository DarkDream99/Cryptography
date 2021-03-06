from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index, name='RSA'),
    re_path('create_keys(\.html)?/', views.create_keys),
    re_path('send_text(\.html)?/', views.send_text),
    re_path('crypt_text(\.html)?/', views.crypt),
    re_path('decrypt_bits(\.html)?/', views.decrypt),
]
