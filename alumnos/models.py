from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.validators import EmailValidator

class Alumno(models.Model):
    # Información básica
    numero_tarjeta = models.CharField(max_length=20, unique=True, verbose_name="Número de Tarjeta")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    ci = models.CharField(max_length=20, unique=True, verbose_name="Cédula de Identidad")
    fecha_nacimiento = models.DateField()
    
    # Información académica (opcional)
    GRADO_CHOICES = [
        ('1ro', '1er Grado'),
        ('2do', '2do Grado'),
        ('3ro', '3er Grado'),
        ('4to', '4to Grado'),
        ('5to', '5to Grado'),
        ('6to', '6to Grado'),
    ]
    grado = models.CharField(max_length=5, choices=GRADO_CHOICES, blank=True, null=True, verbose_name="Grado")
    seccion = models.CharField(max_length=2, blank=True, null=True, verbose_name="Sección")
    
    # Información financiera
    saldo_tarjeta = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Relación con padres/tutores
    padre_tutor = models.ForeignKey(
        'Padre',
        on_delete=models.CASCADE,
        related_name='hijos',
        null=True,
        blank=True,
        verbose_name="Padre/Tutor"
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


class Padre(models.Model):
    """Modelo para datos de facturación legal de padres/tutores"""
    
    # Información personal básica
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, verbose_name="Apellido")
    ci = models.CharField(max_length=20, unique=True, verbose_name="Cédula de Identidad")
    
    # Datos para facturación legal (requeridos)
    ruc = models.CharField(max_length=20, unique=True, verbose_name="RUC")
    razon_social = models.CharField(max_length=200, verbose_name="Razón Social")
    email = models.EmailField(verbose_name="Correo Electrónico", validators=[EmailValidator()])
    celular = models.CharField(max_length=20, verbose_name="Celular")
    
    # Información adicional opcional
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    telefono_fijo = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono Fijo")
    
    # Campos de auditoría
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Padre/Tutor'
        verbose_name_plural = 'Padres/Tutores'
        ordering = ['apellido', 'nombre']
        indexes = [
            models.Index(fields=['ruc']),
            models.Index(fields=['ci']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre} - {self.ruc}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class Curso(models.Model):
    """Modelo para cursos académicos"""
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Curso")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class TransaccionTarjeta(models.Model):
    """Modelo para transacciones de tarjeta"""
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='transacciones_tarjeta')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = 'Transacción de Tarjeta'
        verbose_name_plural = 'Transacciones de Tarjeta'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.alumno.nombre_completo} - ₲{self.monto}"


class Transaccion(models.Model):
    """Modelo general para transacciones"""
    TIPO_CHOICES = [
        ('recarga', 'Recarga'),
        ('compra', 'Compra'),
        ('devolucion', 'Devolución'),
    ]
    
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='transacciones')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.alumno.nombre_completo} - {self.get_tipo_display()} - ₲{self.monto}"
