# productos/admin.py
from django.contrib import admin
from .models import Proveedor, Producto

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto')
    search_fields = ('nombre', 'contacto')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre',
        'categoria',
        'proveedor',
        'precio_costo',
        'precio_venta',
        'cantidad'
    )
    search_fields = ('codigo', 'nombre', 'categoria', 'proveedor__nombre')
    list_filter = ('categoria', 'proveedor')
