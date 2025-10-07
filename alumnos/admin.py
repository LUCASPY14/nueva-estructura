from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Alumno, Padre, Curso, TransaccionTarjeta, Transaccion, SolicitudRecarga

# Definir el inline para TransaccionTarjeta
class TransaccionInline(admin.TabularInline):
    model = TransaccionTarjeta
    extra = 0
    fields = ('fecha', 'tipo', 'monto', 'descripcion')
    readonly_fields = ('fecha',)
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'numero_matricula', 'curso', 'numero_tarjeta', 'saldo_tarjeta', 'limite_consumo', 'estado')
    search_fields = ('nombre', 'apellido', 'numero_matricula', 'numero_tarjeta')
    list_filter = ('estado', 'curso', 'sexo')
    list_editable = ('limite_consumo',)
    filter_horizontal = ('padres',)
    
    inlines = [TransaccionInline]
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'fecha_nacimiento', 'sexo', 'foto')
        }),
        ('Información Académica', {
            'fields': ('curso', 'numero_matricula', 'estado')
        }),
        ('Sistema de Tarjetas', {
            'fields': ('numero_tarjeta', 'saldo_tarjeta', 'limite_consumo', 'consumo_diario', 'ultimo_consumo')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion')
        }),
        ('Padres', {
            'fields': ('padres',)
        }),
        ('Información Adicional', {
            'fields': ('saldo', 'notas')
        }),
    )
    
    readonly_fields = ('consumo_diario', 'ultimo_consumo')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('saldo_tarjeta',)
        return self.readonly_fields

@admin.register(Padre)
class PadreAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'telefono', 'email')
    search_fields = ('nombre', 'apellido', 'email')
    list_filter = ('fecha_creacion',)
    ordering = ['nombre', 'apellido']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'telefono', 'email', 'direccion')
        }),
    )

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(TransaccionTarjeta)
class TransaccionTarjetaAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'fecha', 'tipo', 'monto', 'descripcion')
    list_filter = ('tipo', 'fecha')
    search_fields = ('alumno__nombre', 'alumno__apellido', 'descripcion')
    date_hierarchy = 'fecha'

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = [
        'alumno', 'tipo', 'monto', 'estado', 
        'fecha', 'usuario_responsable'
    ]
    list_filter = [
        'tipo', 'estado', 'fecha',
        ('fecha', admin.DateFieldListFilter),
    ]
    search_fields = [
        'alumno__nombre', 'alumno__apellido', 
        'alumno__numero_matricula', 'descripcion'
    ]
    readonly_fields = ['fecha']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('alumno', 'tipo', 'estado', 'monto', 'descripcion')
        }),
        ('Control de Saldo', {
            'fields': ('saldo_anterior', 'saldo_posterior')
        }),
        ('Referencias', {
            'fields': ('referencia_venta', 'referencia_solicitud', 'numero_comprobante'),
            'classes': ('collapse',)
        }),
        ('Fechas y Usuario', {
            'fields': ('fecha', 'usuario_responsable')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'alumno', 'usuario_responsable'
        )


@admin.register(SolicitudRecarga)
class SolicitudRecargaAdmin(admin.ModelAdmin):
    list_display = [
        'alumno', 'padre_solicitante', 'monto_solicitado', 
        'metodo_pago', 'estado', 'fecha_solicitud'
    ]
    list_filter = [
        'estado', 'metodo_pago',
        ('fecha_solicitud', admin.DateFieldListFilter),
    ]
    search_fields = [
        'alumno__nombre', 'alumno__apellido',
        'padre_solicitante__first_name', 'padre_solicitante__last_name'
    ]
    readonly_fields = ['fecha_solicitud', ]
    
    fieldsets = (
        ('Solicitud', {
            'fields': ('alumno', 'padre_solicitante', 'monto_solicitado', 'metodo_pago')
        }),
        ('Estado', {
            'fields': ('estado', 'fecha_solicitud')
        }),
        ('Comprobante', {
            'fields': ('comprobante_pago', 'numero_comprobante')
        }),
        ('Procesamiento', {
            'fields': ('usuario_procesador', 'observaciones_procesamiento', ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['aprobar_solicitudes', 'procesar_solicitudes']
    
    def aprobar_solicitudes(self, request, queryset):
        """Acción para aprobar solicitudes pendientes"""
        count = 0
        for solicitud in queryset.filter(estado='pendiente'):
            solicitud.estado = 'aprobada'
            solicitud.save()
            count += 1
        
        self.message_user(request, f'{count} solicitudes aprobadas.')
    aprobar_solicitudes.short_description = "Aprobar solicitudes seleccionadas"
    
    def procesar_solicitudes(self, request, queryset):
        """Acción para procesar solicitudes aprobadas"""
        count = 0
        for solicitud in queryset.filter(estado='aprobada'):
            try:
                solicitud.procesar_recarga(
                    usuario_procesador=request.user,
                    observaciones="Procesado desde admin"
                )
                count += 1
            except Exception as e:
                self.message_user(request, f'Error procesando solicitud {solicitud.id}: {e}', level='ERROR')
        
        self.message_user(request, f'{count} solicitudes procesadas.')
    procesar_solicitudes.short_description = "Procesar solicitudes seleccionadas"

# Personalización del admin site
admin.site.site_header = "Administración - Sistema de Cantina"
admin.site.site_title = "Admin Cantina"
admin.site.index_title = "Panel de Administración"
