from django.contrib import admin
from .models import ConfiguracionSistema

@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ('nombre_sistema', 'moneda', 'limite_credito', 'horario_atencion')
    fieldsets = (
        ('Información General', {
            'fields': ('nombre_sistema', 'logo')
        }),
        ('Configuración Financiera', {
            'fields': ('moneda', 'limite_credito')
        }),
        ('Configuración Operativa', {
            'fields': ('horario_atencion',)
        }),
        ('Personalización', {
            'fields': ('color_principal',)
        })
    )