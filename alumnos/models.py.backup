from django.db import models
from django.utils import timezone
from django.conf import settings

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class Padre(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Padre"
        verbose_name_plural = "Padres"
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def get_nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

class Alumno(models.Model):
    # Opciones para campos de selección
    SEXO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    )
    
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    )
    
    # Campos de información personal
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    foto = models.ImageField(upload_to='alumnos/fotos/', blank=True, null=True)
    
    # Campos académicos
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, null=True, blank=True)
    numero_matricula = models.CharField(max_length=20, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    
    # Información de contacto
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    
    # Campos para el sistema de tarjetas de cantina
    numero_tarjeta = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        unique=True, 
        help_text="Número único de la tarjeta del alumno"
    )
    saldo_tarjeta = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Saldo disponible en la tarjeta"
    )
    limite_consumo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Límite diario de consumo (0 = sin límite)"
    )
    ultimo_consumo = models.DateTimeField(blank=True, null=True)
    consumo_diario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Monto consumido en el día actual"
    )
    
    # Otros campos
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Campo para relación con padres
    padres = models.ManyToManyField(Padre, related_name='alumnos', blank=True)
    
    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"
        ordering = ['apellido', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    def get_nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def get_saldo_formateado(self):
        return f"₱{self.saldo_tarjeta:,.0f}"


class SolicitudRecarga(models.Model):
    """Modelo para solicitudes de recarga de saldo"""
    
    ESTADOS_SOLICITUD = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('procesada', 'Procesada'),
    ]
    
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('cheque', 'Cheque'),
        ('deposito', 'Depósito Bancario'),
        ('otro', 'Otro'),
    ]
    
    # Relaciones
    alumno = models.ForeignKey(
        'Alumno',
        on_delete=models.CASCADE,
        related_name='solicitudes_recarga',
        verbose_name="Alumno"
    )
    padre_solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_realizadas',
        verbose_name="Padre solicitante"
    )
    
    # Información de la solicitud
    monto_solicitado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monto solicitado",
        help_text="Monto a recargar en guaraníes"
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS_PAGO,
        default='efectivo',
        verbose_name="Método de pago"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_SOLICITUD,
        default='pendiente',
        verbose_name="Estado"
    )
    
    # Fechas
    fecha_solicitud = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de solicitud"
    )
    fecha_procesamiento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de procesamiento"
    )
    
    # Comprobante
    comprobante_pago = models.ImageField(
        upload_to='comprobantes_recarga/',
        null=True,
        blank=True,
        verbose_name="Comprobante de pago",
        help_text="Subir imagen del comprobante de pago"
    )
    numero_comprobante = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Número de comprobante"
    )
    referencia_pago = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Número de referencia del pago"
    )
    
    # Procesamiento
    usuario_procesador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_procesadas',
        verbose_name="Procesado por"
    )
    observaciones_procesamiento = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones del procesamiento"
    )
    monto_aprobado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name="Monto aprobado"
    )
    
    class Meta:
        verbose_name = "Solicitud de Recarga"
        verbose_name_plural = "Solicitudes de Recarga"
        ordering = ['-fecha_solicitud']
        indexes = [
            models.Index(fields=['estado', 'fecha_solicitud']),
            models.Index(fields=['alumno', 'estado']),
        ]
    
    def __str__(self):
        return f"Recarga {self.alumno.get_nombre_completo()} - ₱{self.monto_solicitado:,.0f} ({self.get_estado_display()})"
    
    def get_monto_formateado(self):
        return f"₱{self.monto_solicitado:,.0f}"
    
    def get_estado_color(self):
        colors = {
            'pendiente': 'warning',
            'aprobada': 'info',
            'rechazada': 'danger',
            'procesada': 'success',
        }
        return colors.get(self.estado, 'secondary')
    
    def puede_ser_procesada(self):
        return self.estado in ['pendiente', 'aprobada']


class Transaccion(models.Model):
    """Modelo para registrar todas las transacciones de saldo"""
    
    TIPOS_TRANSACCION = [
        ('recarga', 'Recarga de Saldo'),
        ('consumo', 'Consumo'),
        ('ajuste', 'Ajuste Manual'),
        ('devolucion', 'Devolución'),
    ]
    
    ESTADOS_TRANSACCION = [
        ('completada', 'Completada'),
        ('pendiente', 'Pendiente'),
        ('cancelada', 'Cancelada'),
        ('error', 'Error'),
    ]
    
    # Relaciones principales
    alumno = models.ForeignKey(
        'Alumno', 
        on_delete=models.CASCADE,
        related_name='transacciones_saldo',
        verbose_name="Alumno"
    )
    
    # Información de la transacción
    tipo = models.CharField(
        max_length=20, 
        choices=TIPOS_TRANSACCION,
        default='consumo',
        verbose_name="Tipo de transacción"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_TRANSACCION,
        default='completada',
        verbose_name="Estado"
    )
    monto = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Monto",
        help_text="Monto de la transacción en guaraníes"
    )
    descripcion = models.CharField(
        max_length=200,
        verbose_name="Descripción",
        help_text="Descripción detallada de la transacción"
    )
    
    # Control de saldo
    saldo_anterior = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Saldo anterior",
        help_text="Saldo antes de la transacción"
    )
    saldo_posterior = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Saldo posterior",
        help_text="Saldo después de la transacción"
    )
    
    # Fechas y usuario
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora"
    )
    usuario_responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacciones_realizadas',
        verbose_name="Usuario responsable"
    )
    
    # Referencias opcionales
    referencia_solicitud = models.ForeignKey(
        'SolicitudRecarga',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Solicitud asociada"
    )
    numero_comprobante = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Número de comprobante"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    
    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['alumno', 'fecha']),
            models.Index(fields=['tipo', 'estado']),
            models.Index(fields=['fecha']),
        ]
        
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.alumno.get_nombre_completo()} - ₱{self.monto:,.0f}"
    
    def save(self, *args, **kwargs):
        # Auto-calcular saldo posterior si no se proporciona
        if not self.saldo_posterior:
            if self.tipo in ['recarga', 'devolucion']:
                self.saldo_posterior = self.saldo_anterior + self.monto
            else:
                self.saldo_posterior = self.saldo_anterior - self.monto
        
        super().save(*args, **kwargs)
        
        # Actualizar saldo del alumno si está completada
        if self.estado == 'completada':
            self.alumno.saldo_tarjeta = self.saldo_posterior
            self.alumno.save(update_fields=['saldo_tarjeta'])
    
    def get_monto_formateado(self):
        return f"₱{self.monto:,.0f}"
    
    def get_tipo_icon(self):
        icons = {
            'recarga': '💳',
            'consumo': '🛒',
            'ajuste': '⚙️',
            'devolucion': '↩️',
        }
        return icons.get(self.tipo, '💰')


# Mantener TransaccionTarjeta por compatibilidad (por ahora)
class TransaccionTarjeta(models.Model):
    """Modelo legacy - usar Transaccion para nuevos desarrollos"""
    TIPO_CHOICES = (
        ('recarga', 'Recarga de Saldo'),
        ('consumo', 'Consumo en Cantina'),
        ('ajuste', 'Ajuste Administrativo'),
    )
    
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='transacciones_tarjeta')
    fecha = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = "Transacción de Tarjeta (Legacy)"
        verbose_name_plural = "Transacciones de Tarjeta (Legacy)"
        
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.alumno} - ₱{self.monto:,.0f}"