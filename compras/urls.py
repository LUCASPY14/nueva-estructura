from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    # Estandarizar nombres de URL
    path('', views.compras_lista, name='lista'),
    path('crear/', views.crear_compra, name='crear'),
    path('editar/<int:pk>/', views.editar_compra, name='editar'),
    path('detalle/<int:pk>/', views.detalle_compra, name='detalle'),
    path('eliminar/<int:pk>/', views.eliminar_compra, name='eliminar'),
]
