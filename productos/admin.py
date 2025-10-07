from django.contrib import admin
from .models import Producto, Categoria, MovimientoStock

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa', 'descripcion')
    list_filter = ('activa',)
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'precio_venta', 'precio_costo', 'cantidad', 'categoria', 'proveedor', 'stock_actual')
    list_filter = ('categoria', 'proveedor', 'estado')
    search_fields = ('nombre', 'codigo', 'codigo_barras')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'stock_actual')

@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo_movimiento', 'cantidad', 'fecha', 'usuario')
    list_filter = ('tipo_movimiento', 'fecha')
    search_fields = ('producto__nombre',)