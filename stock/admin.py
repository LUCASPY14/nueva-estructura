from django.contrib import admin
from .models import MovimientoStock

@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad', 'tipo', 'referencia', 'fecha')
    list_filter = ('tipo', 'producto')
    search_fields = ('producto__nombre', 'referencia')
    date_hierarchy = 'fecha'
