from django.urls import path
from . import views

app_name = 'ayuda'

urlpatterns = [
    path('', views.ayuda_view, name='index'),
    path('contacto/', views.contacto_view, name='contacto'),
]
