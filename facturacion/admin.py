from django.contrib import admin
from .models import Factura

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'venta', 'fecha_emision')
    search_fields = ('numero', 'venta__id', 'venta__alumno__nombre')
    list_filter = ('fecha_emision',)