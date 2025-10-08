from django.contrib import admin
from .models import ConfiguracionSistema

@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ('clave', 'valor', 'activo')
    list_filter = ('activo',)
    search_fields = ('clave', 'valor')
    ordering = ('clave',)
