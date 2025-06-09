from django.contrib import admin
from .models import AuthorizationCode, Venta, DetalleVenta, Pago

@admin.register(AuthorizationCode)
class AuthCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'is_active', 'created')
    actions = ['activar', 'desactivar']

    def activar(self, request, queryset):
        queryset.update(is_active=True)
    activar.short_description = "Marcar como activos"

    def desactivar(self, request, queryset):
        queryset.update(is_active=False)
    desactivar.short_description = "Marcar como inactivos"


class DetalleInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    readonly_fields = ('subtotal_display',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal_display')

    def subtotal_display(self, obj):
        return obj.subtotal()
    subtotal_display.short_description = "Subtotal"


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'alumno', 'cajero', 'fecha', 'total', 'condicion', 'sobregiro_autorizado')
    list_filter = ('condicion', 'sobregiro_autorizado')
    inlines = [DetalleInline, PagoInline]

    def save_model(self, request, obj, form, change):
        # Recalcula total antes de guardar
        super().save_model(request, obj, form, change)
        obj.total = sum(d.subtotal() for d in obj.detalles.all())
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        total = 0
        for instance in instances:
            if isinstance(instance, DetalleVenta):
                total += instance.subtotal()
            instance.save()

        form.instance.total = total
        form.instance.save()
        formset.save_m2m()
