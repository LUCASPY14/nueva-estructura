from django.contrib import admin
from .models import MovimientoStock

@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'producto', 'tipo', 'cantidad', 'referencia')
    list_filter = ('tipo', 'fecha', 'producto')
    search_fields = ('producto__nombre', 'motivo', 'referencia')
    readonly_fields = ('fecha',)
    actions = ['aplicar_movimientos']

    def aplicar_movimientos(self, request, queryset):
        for mov in queryset:
            mov.aplicar()
        self.message_user(request, f"Movimientos aplicados: {queryset.count()}")
    aplicar_movimientos.short_description = "Aplicar stock para los movimientos seleccionados"