# compras/admin.py
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
        # Primero guardamos la compra para obtener un ID si es nueva
        super().save_model(request, obj, form, change)
        # Recalculamos el total y volvemos a guardar
        obj.calcular_total()
        obj.save()

    def save_formset(self, request, form, formset, change):
        """
        Cuando se guardan los detalles en el Admin, actualizamos el stock de Productos automáticamente.
        """
        instances = formset.save(commit=False)
        for detalle in instances:
            # Actualizar stock: sumar la cantidad comprada
            producto = detalle.producto
            producto.cantidad += detalle.cantidad
            producto.save()
            detalle.save()
        formset.save_m2m()
        # Luego de guardar detalles, recalculamos total
        compra = form.instance
        compra.calcular_total()
        compra.save()
