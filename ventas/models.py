from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal
from usuarios.models import CustomUser
from alumnos.models import Alumno
from productos.models import Producto
import uuid

class Caja(models.Model):
    """
    Representa una caja física del negocio.
    """
    numero = models.PositiveIntegerField(unique=True, help_text="Número de la caja (1, 2, 3, etc.)")
    nombre = models.CharField(max_length=50, help_text="Nombre descriptivo de la caja")
    ubicacion = models.CharField(max_length=100, blank=True, help_text="Ubicación física de la caja")
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Caja {self.numero} - {self.nombre}"
    
    class Meta:
        verbose_name = "Caja"
        verbose_name_plural = "Cajas"
        ordering = ['numero']

class MetodoPago(models.Model):
    """
    Define los métodos de pago disponibles en el sistema.
    """
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    requiere_referencia = models.BooleanField(default=False, help_text="Indica si requiere número de referencia")
    es_tarjeta_cantina = models.BooleanField(default=False, help_text="Si es tarjeta de cantina (genera recibo interno)")
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición en interfaces")
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        ordering = ['orden', 'nombre']
        
    @classmethod
    def get_metodos_facturables(cls):
        """Retorna métodos de pago que generan factura legal (no tarjetas de cantina)"""
        return cls.objects.filter(activo=True, es_tarjeta_cantina=False)
    
    @classmethod
    def get_tarjetas_cantina(cls):
        """Retorna métodos de pago que son tarjetas de cantina"""
        return cls.objects.filter(activo=True, es_tarjeta_cantina=True)
    
    @classmethod
    def get_tarjeta_cantina(cls):
        """Retorna el método de pago de tarjeta exclusiva de cantina"""
        return cls.objects.filter(codigo='tarjeta_cantina', activo=True).first()

class TurnoCajero(models.Model):
    """
    Control de turnos de cajeros. Cada cajero debe abrir/cerrar su turno.
    """
    cajero = models.ForeignKey('usuarios.CustomUser', on_delete=models.PROTECT, related_name='turnos')
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT, related_name='turnos')
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observaciones_apertura = models.TextField(blank=True, null=True)
    observaciones_cierre = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    
    def clean(self):
        # Validar que no haya otro turno activo para la misma caja
        if self.activa and self.fecha_fin is None:  # Cambiar 'activo' por 'activa'
            turnos_activos = TurnoCajero.objects.filter(
                caja=self.caja, 
                activa=True,  # Cambiar 'activo' por 'activa'
                fecha_fin__isnull=True
            ).exclude(pk=self.pk)
            
            if turnos_activos.exists():
                raise ValidationError(f'Ya hay un turno activo en la {self.caja}')
    
    @property
    def total_ventas(self):
        """Calcula el total de ventas durante este turno"""
        return self.ventas.filter(estado='completada').aggregate(
            total=models.Sum('total')
        )['total'] or Decimal('0.00')
    
    @property
    def cantidad_ventas(self):
        """Cantidad de ventas realizadas en el turno"""
        return self.ventas.filter(estado='completada').count()
    
    @property
    def diferencia(self):
        """Calcula la diferencia entre lo esperado y lo contado"""
        if self.monto_final is not None:
            esperado = self.monto_inicial + self.total_ventas
            return self.monto_final - esperado
        return None
    
    @property
    def duracion(self):
        """Duración del turno"""
        fin = self.fecha_fin or timezone.now()
        return fin - self.fecha_inicio
    
    def cerrar_turno(self, monto_final, observaciones_cierre=""):
        """Cierra el turno del cajero"""
        self.monto_final = monto_final
        self.fecha_fin = timezone.now()
        self.observaciones_cierre = observaciones_cierre
        self.activa = False  # Cambiar 'activo' por 'activa'
        self.save()
    
    def __str__(self):
        return f"{self.cajero.get_full_name()} - {self.caja} ({self.fecha_inicio.strftime('%d/%m/%Y %H:%M')})"
    
    class Meta:
        verbose_name = "Turno de Cajero"
        verbose_name_plural = "Turnos de Cajeros"
        ordering = ['-fecha_inicio']

class Venta(models.Model):
    """Modelo para registrar ventas con lógica de facturación diferenciada"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    TIPO_COMPROBANTE_CHOICES = [
        ('factura', 'Factura Legal'),
        ('comprobante_interno', 'Comprobante Interno'),
        ('sin_comprobante', 'Sin Comprobante'),
        ('factura_parcial', 'Factura por Diferencia'), # Para pagos mixtos
    ]
    
    # Campos básicos
    numero_venta = models.CharField(max_length=20, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('usuarios.CustomUser', on_delete=models.PROTECT, related_name='ventas')
    alumno = models.ForeignKey('alumnos.Alumno', on_delete=models.PROTECT, related_name='compras', null=True, blank=True)
    turno_cajero = models.ForeignKey(TurnoCajero, on_delete=models.PROTECT, related_name='ventas', null=True, blank=True)
    
    # Totales
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    descuento = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    
    # Pagos y facturación
    monto_tarjeta_cantina = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text="Monto pagado con tarjeta exclusiva de cantina"
    )
    monto_otros_medios = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text="Monto pagado con otros medios (efectivo, tarjetas, etc.)"
    )
    
    # Estado y comprobantes
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    tipo_comprobante = models.CharField(max_length=20, choices=TIPO_COMPROBANTE_CHOICES, null=True, blank=True)
    numero_factura = models.CharField(max_length=30, null=True, blank=True, help_text="Número de factura legal")
    numero_comprobante_interno = models.CharField(max_length=30, null=True, blank=True)
    
    # Campos adicionales
    notas = models.TextField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['numero_venta']),
            models.Index(fields=['fecha']),
            models.Index(fields=['estado']),
            models.Index(fields=['usuario']),
        ]

    def __str__(self):
        return f"Venta {self.numero_venta} - {self.fecha.strftime('%d/%m/%Y')}"
    
    @property
    def es_pago_mixto(self):
        """Determina si es un pago mixto (tarjeta cantina + otros medios)"""
        return self.monto_tarjeta_cantina > 0 and self.monto_otros_medios > 0
    
    @property
    def es_solo_tarjeta_cantina(self):
        """Determina si el pago es únicamente con tarjeta de cantina"""
        return self.monto_tarjeta_cantina > 0 and self.monto_otros_medios == 0
    
    @property
    def requiere_factura_legal(self):
        """Determina si requiere factura legal según el tipo de pago"""
        if self.es_solo_tarjeta_cantina:
            return False  # Solo comprobante interno
        elif self.es_pago_mixto:
            return True   # Factura por la diferencia (monto_otros_medios)
        else:
            return True   # Factura completa para otros medios de pago
    
    @property
    def monto_factura(self):
        """Calcula el monto que debe facturarse legalmente"""
        if self.es_solo_tarjeta_cantina:
            return Decimal('0.00')  # No se factura
        elif self.es_pago_mixto:
            return self.monto_otros_medios  # Solo la diferencia
        else:
            return self.total  # Monto completo
    
    def determinar_tipo_comprobante(self):
        """Determina el tipo de comprobante según la lógica de negocio"""
        if self.es_solo_tarjeta_cantina:
            return 'comprobante_interno'
        elif self.es_pago_mixto:
            return 'factura_parcial'
        else:
            return 'factura'
    
    def clean(self):
        """Validaciones del modelo"""
        super().clean()
        
        # La suma de los pagos debe igualar el total
        total_pagado = self.monto_tarjeta_cantina + self.monto_otros_medios
        if total_pagado != self.total:
            raise ValidationError(
                f'La suma de los pagos ({total_pagado}) debe igualar el total ({self.total})'
            )
    
    def save(self, *args, **kwargs):
        if not self.numero_venta:
            # Generar número de venta automáticamente
            from django.utils import timezone
            today = timezone.now()
            count = Venta.objects.filter(fecha__date=today.date()).count() + 1
            self.numero_venta = f"V{today.strftime('%Y%m%d')}{count:04d}"
        
        # Determinar el tipo de comprobante automáticamente
        if not self.tipo_comprobante:
            self.tipo_comprobante = self.determinar_tipo_comprobante()
        
        super().save(*args, **kwargs)


class PagoVenta(models.Model):
    """Modelo para registrar los diferentes métodos de pago de una venta"""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='pagos')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    monto = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    referencia = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        help_text="Número de referencia, cheque, transferencia, etc."
    )
    aprobado = models.BooleanField(default=True)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Pago de Venta'
        verbose_name_plural = 'Pagos de Ventas'
        ordering = ['fecha_pago']
        indexes = [
            models.Index(fields=['venta']),
            models.Index(fields=['metodo_pago']),
            models.Index(fields=['fecha_pago']),
        ]
    
    def __str__(self):
        return f"{self.venta.numero_venta} - {self.metodo_pago.nombre}: ₲{self.monto}"
    
    def clean(self):
        """Validaciones del modelo"""
        super().clean()
        
        # Validar que se proporcione referencia si es requerida
        if self.metodo_pago.requiere_referencia and not self.referencia:
            raise ValidationError(
                f'El método de pago {self.metodo_pago.nombre} requiere número de referencia'
            )

class DetalleVenta(models.Model):
    """Detalle de productos en una venta"""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT, related_name='ventas_detalle')
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    
    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Ventas'
        unique_together = ['venta', 'producto']
        indexes = [
            models.Index(fields=['venta']),
            models.Index(fields=['producto']),
        ]
    
    def __str__(self):
        return f"{self.venta.numero_venta} - {self.producto.nombre}"
    
    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

class PagoVenta(models.Model):
    """
    Registra los pagos realizados para una venta.
    """
    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('QR_WALLET', 'QR/Wallet'),
        ('SALDO', 'Saldo prepago'),
        ('CHEQUE', 'Cheque'),
        ('OTRO', 'Otro'),
    ]
    
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='pagos')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, null=True, blank=True)
    metodo = models.CharField(max_length=20, choices=METODOS_PAGO, default='EFECTIVO')
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    tasa = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Tasa de comisión (%)")
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monto + comisión")
    referencia = models.CharField(max_length=100, blank=True, null=True, help_text="Número de comprobante/referencia")
    observacion = models.CharField(max_length=255, blank=True, null=True)
    fecha = models.DateTimeField(default=timezone.now)
    aprobado = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if self.monto <= 0:
            raise ValueError("El monto debe ser mayor a cero.")
        
        # Calcular tasa según método de pago
        if self.metodo == 'TARJETA_CREDITO':
            self.tasa = Decimal('5.0')
        elif self.metodo == 'TARJETA_DEBITO':
            self.tasa = Decimal('2.0')
        elif self.metodo == 'QR_WALLET':
            self.tasa = Decimal('1.5')
        else:
            self.tasa = Decimal('0.0')
        
        # Calcular monto final con comisión
        self.monto_final = self.monto + (self.monto * self.tasa / 100)
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validaciones adicionales"""
        super().clean()
        
        # Validar que el monto no exceda el total de la venta
        if self.venta_id:
            total_pagos = self.venta.pagos.exclude(pk=self.pk).aggregate(
                total=models.Sum('monto')
            )['total'] or Decimal('0')
            
            if (total_pagos + self.monto) > self.venta.total:
                raise ValidationError(
                    f'El total de pagos (${total_pagos + self.monto}) '
                    f'excede el total de la venta (${self.venta.total})'
                )
        
        # Validar referencia para métodos que la requieren
        if self.metodo in ['TARJETA_CREDITO', 'TARJETA_DEBITO', 'TRANSFERENCIA'] and not self.referencia:
            raise ValidationError(f'El método {self.get_metodo_display()} requiere número de referencia')
    
    @property
    def comision(self):
        """Calcula la comisión del pago"""
        return self.monto_final - self.monto
    
    def __str__(self):
        return f"{self.get_metodo_display()}: ${self.monto} (Venta {self.venta.numero_venta})"
    
    class Meta:
        verbose_name = "Pago de Venta"
        verbose_name_plural = "Pagos de Venta"
        ordering = ['-fecha']

class AuthorizationCode(models.Model):
    """
    Código de autorización especial asociado a una venta.
    """
    codigo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='autorizaciones')
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.codigo} - {self.venta} ({self.fecha:%d/%m/%Y})"

    class Meta:
        ordering = ['-fecha']
        verbose_name_plural = "Códigos de autorización"

class ReporteCaja(models.Model):
    """
    Reporte consolidado de caja por día/turno.
    """
    fecha = models.DateField()
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT)
    turnos_total = models.PositiveIntegerField(default=0)
    ventas_total = models.PositiveIntegerField(default=0)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    diferencias_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    generado_el = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reporte {self.caja} - {self.fecha}"
    
    class Meta:
        verbose_name = "Reporte de Caja"
        verbose_name_plural = "Reportes de Caja"
        unique_together = ['fecha', 'caja']
        ordering = ['-fecha', 'caja']

# FIN DEL ARCHIVO - NO AGREGAR MÁS CÓDIGO AQUÍ
