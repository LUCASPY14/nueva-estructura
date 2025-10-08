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
    readonly_fields = ['subtotal']

class PagoVentaInline(admin.TabularInline):
    model = PagoVenta
    extra = 1
    fields = ('metodo', 'monto', 'referencia')

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = [
        'numero_venta', 
        'fecha', 
        'usuario', 
        'alumno', 
        'total', 
        'estado',
        'tipo_pago'
    ]
    list_filter = [
        'estado', 
        'tipo_pago',  # Corregido: quitamos campos inexistentes
        'fecha',
        'usuario'
    ]
    search_fields = ['numero_venta', 'alumno__nombre', 'alumno__apellido']
    readonly_fields = ['numero_venta', 'fecha', 'fecha_actualizacion']
    ordering = ['-fecha']
    inlines = [DetalleVentaInline]
    
    fieldsets = (
        ('Información de Venta', {
            'fields': ('numero_venta', 'fecha', 'usuario', 'alumno')
        }),
        ('Totales', {
            'fields': ('subtotal', 'descuento', 'total')
        }),
        ('Estado', {
            'fields': ('estado', 'tipo_pago', 'notas')
        }),
        ('Fechas', {
            'fields': ('fecha_actualizacion',),
            'classes': ('collapse',)
        }),
    )

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['venta__fecha', 'producto__categoria']
    search_fields = ['venta__numero_venta', 'producto__nombre']
    readonly_fields = ['subtotal']

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
