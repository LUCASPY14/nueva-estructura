# productos/urls.py
from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    # Rutas para PRODUCTOS
    path('lista/', views.productos_lista, name='listar_productos'),
    path('crear/', views.crear_producto, name='crear_producto'),
    path('editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),

    # Rutas para PROVEEDORES (opcionales)
    path('proveedores/', views.proveedores_lista, name='listar_proveedores'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/editar/<int:pk>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/<int:pk>/', views.eliminar_proveedor, name='eliminar_proveedor'),
]
