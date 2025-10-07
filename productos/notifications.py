from django.db import models
from django.conf import settings
from django.utils import timezone

class StockNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('stock_bajo', 'Stock Bajo'),
        ('agotado', 'Producto Agotado'),
        ('reorden', 'Punto de Reorden'),
    ]
    
    PRIORITY_LEVELS = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    tipo = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    mensaje = models.TextField()
    prioridad = models.CharField(max_length=10, choices=PRIORITY_LEVELS)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    destinatarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='notificaciones_stock'
    )
    
    class Meta:
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['-fecha_creacion']),
            models.Index(fields=['tipo']),
            models.Index(fields=['prioridad']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre}"
    
    def marcar_como_leida(self, usuario):
        """Marca la notificación como leída para un usuario específico"""
        self.destinatarios.remove(usuario)
        if not self.destinatarios.exists():
            self.fecha_lectura = timezone.now()
            self.save()
    
    @property
    def esta_leida(self):
        """Retorna True si la notificación ha sido leída"""
        return self.fecha_lectura is not None