from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'precio_venta', 'precio_costo', 'cantidad', 'categoria', 'proveedor', 'stock_actual')
    search_fields = ('nombre', 'codigo')