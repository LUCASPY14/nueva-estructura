# app/ventas/admin.py
from django.contrib import admin
from .models import Venta, DetalleVenta
from stock.models import MovimientoStock

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    readonly_fields = ('subtotal_display',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal_display')
    can_delete = True

    def subtotal_display(self, obj):
        return obj.subtotal()
    subtotal_display.short_description = "Subtotal"

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'alumno', 'fecha', 'total')
    search_fields = ('alumno__nombre',)
    list_filter = ('fecha',)
    inlines = [DetalleVentaInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calcular_total()
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for detalle in instances:
            detalle.save()
            # Solo crear movimiento si es una nueva línea
            if detalle.pk is None:
                MovimientoStock.objects.create(
                    producto=detalle.producto,
                    cantidad=-detalle.cantidad,  # Negativo porque es egreso
                    motivo='Venta',
                    venta=form.instance,
                    usuario=request.user
                )
        formset.save_m2m()
        venta = form.instance
        venta.calcular_total()
        venta.save()
