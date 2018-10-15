from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index, name='RSA'),
    re_path('create_keys(\.html)?/change_keys/', views.change_key),
    re_path('create_keys(\.html)?/', views.create_keys),
    re_path('swap_keys(\.html)?/server_key/', views.server_key),
    re_path('swap_keys(\.html)?/set_server_url/', views.change_server_url),
    re_path('swap_keys(\.html)?/public_keys/', views.public_keys),
    re_path('swap_keys(\.html)?/', views.gener_swap_keys),
    re_path('send_text(\.html)?/', views.change_text),
    re_path('crypt_text(\.html)?/', views.crypt),
    re_path('decrypt_bits(\.html)?/', views.decrypt),
]
