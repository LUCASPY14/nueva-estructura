from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal
from usuarios.models import UsuarioLG
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
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        ordering = ['nombre']

class TurnoCajero(models.Model):
    """
    Control de turnos de cajeros. Cada cajero debe abrir/cerrar su turno.
    """
    cajero = models.ForeignKey('usuarios.UsuarioLG', on_delete=models.PROTECT, related_name='turnos')
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
    """
    Representa una venta realizada en el punto de venta.
    """
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('anulada', 'Anulada'),
    ]
    
    class Meta:
        indexes = [
            models.Index(fields=['fecha', 'estado']),
            models.Index(fields=['turno', 'estado']),
            models.Index(fields=['cliente', 'estado']),
            models.Index(fields=['fecha', 'estado', 'turno']),
        ]
        ordering = ['-fecha']class DetalleVenta(models.Model):
    """
    Representa un item individual dentro de una venta.
    """
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0.001)], default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    @property
    def subtotal(self):
        """Calcula el subtotal del item"""
        # Validar que los valores no sean None
        cantidad = self.cantidad or Decimal('0')
        precio = self.precio_unitario or Decimal('0')
        descuento = self.descuento_item or Decimal('0')
        
        return (cantidad * precio) - descuento
    
    def save(self, *args, **kwargs):
        # Si no se especifica precio, usar el precio de venta del producto
        if not self.precio_unitario and self.producto:
            self.precio_unitario = self.producto.precio_venta
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validaciones adicionales para el detalle"""
        super().clean()
    
        # Validar cantidad positiva
        if self.cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a cero.')
    
        # Validar precio positivo
        if self.precio_unitario < 0:
            raise ValidationError('El precio unitario no puede ser negativo.')
    
        # Validar que haya stock disponible
        if self.producto and self.producto.cantidad < self.cantidad:
            raise ValidationError(f'Stock insuficiente. Disponible: {self.producto.cantidad}')
    
        # Validar que el descuento no sea mayor al subtotal antes del descuento
        subtotal_sin_descuento = self.cantidad * self.precio_unitario
        if self.descuento_item > subtotal_sin_descuento:
            raise ValidationError('El descuento del item no puede ser mayor al subtotal.')
    
    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
    
    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

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
