from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Alumno(models.Model):
    # Información básica
    numero_tarjeta = models.CharField(max_length=20, unique=True, verbose_name="Número de Tarjeta")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    ci = models.CharField(max_length=20, unique=True, verbose_name="Cédula de Identidad")
    fecha_nacimiento = models.DateField()
    
    # Información académica
    GRADO_CHOICES = [
        ('1ro', '1er Grado'),
        ('2do', '2do Grado'),
        ('3ro', '3er Grado'),
        ('4to', '4to Grado'),
        ('5to', '5to Grado'),
        ('6to', '6to Grado'),
    ]
    grado = models.CharField(max_length=5, choices=GRADO_CHOICES)
    seccion = models.CharField(max_length=2, default='A')
    
    # Información financiera
    saldo_tarjeta = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Relación con padres/tutores - usar settings.AUTH_USER_MODEL
    padre_tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hijos',
        null=True,
        blank=True
    )
    
    # Campos de auditoría
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'
        ordering = ['apellido', 'nombre']
        indexes = [
            models.Index(fields=['numero_tarjeta']),
            models.Index(fields=['ci']),
        ]
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre} - {self.numero_tarjeta}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    @property
    def puede_comprar(self):
        return self.activo and self.saldo_tarjeta > 0

class MovimientoSaldo(models.Model):
    TIPO_MOVIMIENTO = [
        ('carga', 'Carga de Saldo'),
        ('compra', 'Compra'),
        ('ajuste', 'Ajuste Manual'),
        ('devolucion', 'Devolución'),
    ]
    
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_nuevo = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    
    # Usuario que realizó el movimiento - usar settings.AUTH_USER_MODEL
    realizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_realizados'
    )
    
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Movimiento de Saldo'
        verbose_name_plural = 'Movimientos de Saldo'
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        return f"{self.alumno.nombre_completo} - {self.get_tipo_display()} - ₲{self.monto}"

class SolicitudRecarga(models.Model):
    """Solicitudes de recarga de saldo por parte de padres"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='solicitudes_recarga')
    padre = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_recarga'
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    
    # Campos de auditoría
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    procesado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_procesadas'
    )
    
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Solicitud de Recarga'
        verbose_name_plural = 'Solicitudes de Recarga'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.alumno.nombre_completo} - ₲{self.monto} - {self.get_estado_display()}"
