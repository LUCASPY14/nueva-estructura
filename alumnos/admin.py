from django.contrib import admin
from .models import Alumno, Padre

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('numero_tarjeta', 'apellido', 'nombre', 'saldo_tarjeta', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'apellido', 'numero_tarjeta')

@admin.register(Padre)
class PadreAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'ruc', 'razon_social', 'email')
    search_fields = ('nombre', 'apellido', 'ruc', 'email')
