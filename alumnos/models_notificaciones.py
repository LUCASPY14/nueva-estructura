from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

class Notificacion(models.Model):
    """Modelo para gestionar notificaciones en el sistema"""
    
    TIPO_CHOICES = [
        ('saldo_bajo', 'Saldo Bajo'),
        ('transaccion', 'Nueva Transacción'),
        ('solicitud', 'Solicitud de Recarga'),
        ('limite_consumo', 'Límite de Consumo'),
        ('sistema', 'Sistema'),
    ]
    
    NIVEL_CHOICES = [
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('success', 'Éxito'),
    ]
    
    # Campos básicos
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default='info')
    
    # Destinatario
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    
    # Enlaces genéricos para relacionar con cualquier modelo
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    contenido_relacionado = GenericForeignKey('content_type', 'object_id')
    
    # Control de estado y fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    leida = models.BooleanField(default=False)
    
    # URLs y acciones
    url_accion = models.CharField(max_length=255, blank=True, null=True)
    texto_accion = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', '-fecha_creacion']),
            models.Index(fields=['tipo']),
            models.Index(fields=['leida']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_display()}"
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save()
    
    def get_url_absoluta(self):
        """Retorna la URL absoluta de la acción o del contenido relacionado"""
        if self.url_accion:
            return self.url_accion
            
        if self.contenido_relacionado:
            # Intentar obtener la URL del objeto relacionado
            try:
                return self.contenido_relacionado.get_absolute_url()
            except AttributeError:
                pass
                
        return None
    
    def get_icono(self):
        """Retorna el ícono correspondiente al tipo de notificación"""
        iconos = {
            'saldo_bajo': '💰',
            'transaccion': '💳',
            'solicitud': '📝',
            'limite_consumo': '⚠️',
            'sistema': '🔔',
        }
        return iconos.get(self.tipo, '🔔')
        
    def get_color_clase(self):
        """Retorna la clase CSS para el color según el nivel"""
        colores = {
            'info': 'info',
            'warning': 'warning',
            'error': 'danger',
            'success': 'success',
        }
        return colores.get(self.nivel, 'secondary')
    
    @classmethod
    def crear_notificacion_saldo_bajo(cls, alumno, saldo_actual):
        """Crea una notificación de saldo bajo para el alumno y sus padres"""
        # Notificar al alumno si tiene usuario
        if hasattr(alumno, 'usuario') and alumno.usuario:
            cls.objects.create(
                usuario=alumno.usuario,
                titulo='Saldo Bajo en Tarjeta',
                mensaje=f'Tu saldo actual es ${saldo_actual:,.0f}. Por favor recarga tu tarjeta.',
                tipo='saldo_bajo',
                nivel='warning',
                contenido_relacionado=alumno,
                url_accion=reverse('alumnos:solicitar_recarga')
            )
        
        # Notificar a los padres
        for padre in alumno.padres.all():
            if hasattr(padre, 'usuario') and padre.usuario:
                cls.objects.create(
                    usuario=padre.usuario,
                    titulo=f'Saldo Bajo - {alumno.get_nombre_completo()}',
                    mensaje=f'El saldo de {alumno.nombre} es ${saldo_actual:,.0f}. Por favor realice una recarga.',
                    tipo='saldo_bajo',
                    nivel='warning',
                    contenido_relacionado=alumno,
                    url_accion=reverse('alumnos:solicitar_recarga')
                )
    
    @classmethod
    def crear_notificacion_transaccion(cls, transaccion):
        """Crea una notificación para una nueva transacción"""
        alumno = transaccion.alumno
        monto = transaccion.monto
        tipo = transaccion.get_tipo_display().lower()
        
        # Notificar al alumno
        if hasattr(alumno, 'usuario') and alumno.usuario:
            cls.objects.create(
                usuario=alumno.usuario,
                titulo=f'Nueva {transaccion.get_tipo_display()}',
                mensaje=f'Se ha realizado un {tipo} de ${monto:,.0f}. Saldo actual: ${alumno.saldo_tarjeta:,.0f}',
                tipo='transaccion',
                nivel='info',
                contenido_relacionado=transaccion,
                url_accion=reverse('alumnos:historial_transacciones', args=[alumno.pk])
            )
        
        # Notificar a los padres
        for padre in alumno.padres.all():
            if hasattr(padre, 'usuario') and padre.usuario:
                cls.objects.create(
                    usuario=padre.usuario,
                    titulo=f'Nueva {transaccion.get_tipo_display()} - {alumno.get_nombre_completo()}',
                    mensaje=f'Se ha realizado un {tipo} de ${monto:,.0f} para {alumno.nombre}. Saldo actual: ${alumno.saldo_tarjeta:,.0f}',
                    tipo='transaccion',
                    nivel='info',
                    contenido_relacionado=transaccion,
                    url_accion=reverse('alumnos:historial_transacciones', args=[alumno.pk])
                )
    
    @classmethod
    def crear_notificacion_solicitud(cls, solicitud):
        """Crea notificaciones para una solicitud de recarga"""
        estado = solicitud.get_estado_display().lower()
        
        # Notificar al padre solicitante
        cls.objects.create(
            usuario=solicitud.padre_solicitante,
            titulo=f'Solicitud de Recarga {estado}',
            mensaje=f'Tu solicitud de recarga por ${solicitud.monto_solicitado:,.0f} para {solicitud.alumno.nombre} ha sido {estado}.',
            tipo='solicitud',
            nivel='success' if solicitud.estado == 'aprobada' else 'info',
            contenido_relacionado=solicitud,
            url_accion=reverse('alumnos:mis_solicitudes')
        )
        
        # Si está aprobada, notificar a los administradores
        if solicitud.estado == 'aprobada':
            admins = settings.AUTH_USER_MODEL.objects.filter(is_staff=True)
            for admin in admins:
                cls.objects.create(
                    usuario=admin,
                    titulo=f'Nueva Solicitud de Recarga',
                    mensaje=f'Hay una nueva solicitud de recarga por ${solicitud.monto_solicitado:,.0f} para {solicitud.alumno.nombre}.',
                    tipo='solicitud',
                    nivel='info',
                    contenido_relacionado=solicitud,
                    url_accion=reverse('alumnos:procesar_solicitud', args=[solicitud.pk])
                )
    
    @classmethod
    def crear_notificacion_limite_consumo(cls, alumno, consumo_actual):
        """Crea una notificación cuando se alcanza el límite de consumo diario"""
        mensaje = f'Has alcanzado tu límite de consumo diario de ${alumno.limite_consumo:,.0f}. Consumo actual: ${consumo_actual:,.0f}'
        
        # Notificar al alumno
        if hasattr(alumno, 'usuario') and alumno.usuario:
            cls.objects.create(
                usuario=alumno.usuario,
                titulo='Límite de Consumo Alcanzado',
                mensaje=mensaje,
                tipo='limite_consumo',
                nivel='warning',
                contenido_relacionado=alumno
            )
        
        # Notificar a los padres
        for padre in alumno.padres.all():
            if hasattr(padre, 'usuario') and padre.usuario:
                cls.objects.create(
                    usuario=padre.usuario,
                    titulo=f'Límite de Consumo Alcanzado - {alumno.get_nombre_completo()}',
                    mensaje=f'{alumno.nombre} ha alcanzado su límite de consumo diario de ${alumno.limite_consumo:,.0f}',
                    tipo='limite_consumo',
                    nivel='warning',
                    contenido_relacionado=alumno
                )