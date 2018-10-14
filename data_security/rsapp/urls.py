from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index, name='RSA'),
    re_path('create_keys(\.html)?/', views.create_keys),
    re_path('swap_keys(\.html)?/', views.swap_keys),
    re_path('send_text(\.html)?/', views.change_text),
    re_path('crypt_text(\.html)?/', views.crypt),
]
