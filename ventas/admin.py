# app/ventas/admin.py
from django.contrib import admin
from django.db import transaction
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import (
    Venta, DetalleVenta, MetodoPago, PagoVenta, 
    Caja, TurnoCajero, AuthorizationCode, ReporteCaja
)

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'descuento_item')

class PagoVentaInline(admin.TabularInline):
    model = PagoVenta
    extra = 1
    fields = ('metodo', 'monto', 'referencia')

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        'numero_venta', 'fecha', 'cliente_nombre', 
        'total', 'estado', 'cajero_nombre'
    )
    list_filter = (
        'estado', 'condicion', 'fecha', 'cajero'
    )
    search_fields = (
        'numero_venta', 'cliente__nombre', 'cliente__apellido', 'observaciones'
    )
    inlines = [DetalleVentaInline, PagoVentaInline]
    readonly_fields = ('numero_venta', 'subtotal', 'total')
    
    def cliente_nombre(self, obj):
        if obj.cliente:
            return f"{obj.cliente.nombre} {obj.cliente.apellido}"
        return "Sin cliente"
    cliente_nombre.short_description = "Cliente"
    
    def cajero_nombre(self, obj):
        if obj.cajero:
            return f"{obj.cajero.first_name} {obj.cajero.last_name}"
        return "Sin cajero"
    cajero_nombre.short_description = "Cajero"
    
    def save_related(self, request, form, formsets, change):
        """Después de guardar los items relacionados, recalcular totales"""
        super().save_related(request, form, formsets, change)
        
        venta = form.instance
        if hasattr(venta, 'calcular_totales'):
            venta.calcular_totales()
    
    actions = ['procesar_ventas', 'cancelar_ventas']
    
    def procesar_ventas(self, request, queryset):
        """Procesa las ventas seleccionadas actualizando inventario y saldos"""
        procesadas = 0
        errores = []
        
        for venta in queryset.filter(estado='pendiente'):
            try:
                venta.procesar_venta()
                procesadas += 1
            except ValidationError as e:
                errores.append(f"Venta {venta.numero_venta}: {str(e)}")
            except Exception as e:
                errores.append(f"Venta {venta.numero_venta}: Error inesperado - {str(e)}")
        
        # Mostrar resultados
        if procesadas:
            self.message_user(
                request, 
                f'✅ {procesadas} ventas procesadas exitosamente.',
                messages.SUCCESS
            )
        
        if errores:
            for error in errores:
                self.message_user(request, error, messages.ERROR)
        
        if not procesadas and not errores:
            self.message_user(
                request, 
                'No hay ventas pendientes para procesar.',
                messages.INFO
            )
    
    procesar_ventas.short_description = "✅ Procesar ventas (actualizar stock y saldos)"
    
    def cancelar_ventas(self, request, queryset):
        """Cancela las ventas seleccionadas y revierte cambios si es necesario"""
        canceladas = 0
        errores = []
        
        for venta in queryset.exclude(estado='cancelada'):
            try:
                venta.cancelar_venta("Cancelada desde admin")
                canceladas += 1
            except Exception as e:
                errores.append(f"Venta {venta.numero_venta}: {str(e)}")
        
        # Mostrar resultados
        if canceladas:
            self.message_user(
                request,
                f'❌ {canceladas} ventas canceladas.',
                messages.WARNING
            )
        
        if errores:
            for error in errores:
                self.message_user(request, error, messages.ERROR)
    
    cancelar_ventas.short_description = "❌ Cancelar ventas (revierte cambios)"

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('venta__fecha',)
    search_fields = ('venta__numero_venta', 'producto__nombre')

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo', 'requiere_referencia')
    list_filter = ('activo', 'requiere_referencia')
    search_fields = ('nombre',)

@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nombre', 'ubicacion', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre', 'ubicacion')

@admin.register(TurnoCajero)
class TurnoCajeroAdmin(admin.ModelAdmin):
    list_display = (
        'cajero', 'caja', 'fecha_inicio', 'activa'
    )
    list_filter = ('activa', 'caja', 'fecha_inicio')
    search_fields = ('cajero__first_name', 'cajero__last_name')
    readonly_fields = ('total_ventas', 'cantidad_ventas')

@admin.register(PagoVenta)
class PagoVentaAdmin(admin.ModelAdmin):
    list_display = (
        'venta', 'metodo', 'monto', 'referencia', 'fecha'
    )
    list_filter = ('metodo', 'fecha')
    search_fields = ('venta__numero_venta', 'referencia')

# Registrar solo si existe el modelo
try:
    admin.site.register(ReporteCaja)
except:
    pass
