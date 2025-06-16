from django.contrib import admin
from .models import Compra, DetalleCompra

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1
    readonly_fields = ('subtotal_display',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal_display')
    can_delete = True

    def subtotal_display(self, obj):
        return obj.subtotal()
    subtotal_display.short_description = "Subtotal"

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha', 'total')
    search_fields = ('proveedor__nombre',)
    list_filter = ('proveedor', 'fecha')
    inlines = [DetalleCompraInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calcular_total()
        obj.save()
