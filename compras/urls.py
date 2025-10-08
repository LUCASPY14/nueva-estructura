from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('', views.lista_compras, name='lista'),
    path('nueva/', views.nueva_compra, name='nueva'),
    path('<int:pk>/ver/', views.ver_compra, name='ver'),
    path('ordenes/', views.ordenes_compra, name='ordenes'),
    path('recepcion/', views.recepcion_mercancia, name='recepcion'),
]
