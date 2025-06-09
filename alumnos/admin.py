# alumnos/admin.py
from django.contrib import admin
from .models import Padre, Alumno, Restriccion

@admin.register(Padre)
class PadreAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'ruc', 'email', 'telefono', 'ciudad')
    search_fields = ('nombre', 'apellido', 'razon_social', 'ruc', 'email')
    list_filter = ('ciudad',)

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'numero_tarjeta', 'padre', 
        'grado', 'nivel', 'limite_consumo', 'saldo_tarjeta'
    )
    
    list_filter = ('grado', 'nivel')
    search_fields = ('nombre', 'padre__nombre', 'padre__apellido', 'numero_tarjeta')

@admin.register(Restriccion)
class RestriccionAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'producto', 'permitido')
    list_filter = ('permitido', 'producto')
    search_fields = ('alumno__nombre', 'producto__nombre')
