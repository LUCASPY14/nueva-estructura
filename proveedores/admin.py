from django.contrib import admin
from .models import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'email', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'email', 'telefono')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'activo')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'sitio_web', 'direccion')
        }),
        ('Notas', {
            'fields': ('notas',)
        })
    )
