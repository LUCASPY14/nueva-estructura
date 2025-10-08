from django.contrib import admin
from .models import Categoria, Producto, MovimientoStock

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activa']
    search_fields = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'categoria', 'precio', 'cantidad', 'activo')
    list_filter = ('activo', 'categoria')
    search_fields = ('nombre', 'codigo')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    ordering = ('nombre',)

@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'fecha', 'usuario')
    list_filter = ('tipo', 'fecha')
    search_fields = ('producto__nombre', 'motivo')
    readonly_fields = ('fecha',)
    autocomplete_fields = ('producto', 'usuario')