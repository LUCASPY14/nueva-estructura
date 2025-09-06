from django.db import models
from decimal import Decimal
from alumnos.models import Alumno
from productos.models import Producto
import uuid
from django.conf import settings

class Venta(models.Model):
    """
    Representa una venta realizada a un alumno.
    """
    CONDICIONES = [
        ('CONTADO', 'Contado'),
        ('CREDITO', 'Crédito'),
    ]

    alumno = models.ForeignKey(Alumno, on_delete=models.PROTECT, related_name='ventas')
    condicion = models.CharField(max_length=10, choices=CONDICIONES, default='CONTADO')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cajero = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas_realizadas',
        help_text="Usuario que realizó la venta"
    )

    def actualizar_total(self):
        total = sum(detalle.subtotal() for detalle in self.detalles.all())
        self.total = total
        self.save(update_fields=['total'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.actualizar_total()

    def __str__(self):
        return f"Venta #{self.id} - {self.alumno.nombre} - {self.fecha:%d/%m/%Y}"

    class Meta:
        ordering = ['-fecha']
        verbose_name_plural = "Ventas"

class DetalleVenta(models.Model):
    """
    Detalle de los productos vendidos en una venta.
    """
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        """
        Retorna el subtotal de este ítem (cantidad x precio unitario).
        """
        cantidad = self.cantidad or 0
        precio = self.precio_unitario or Decimal('0.00')
        return cantidad * precio

    @staticmethod
    def total_venta(venta):
        return sum(detalle.subtotal() for detalle in venta.detalles.all())

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

    class Meta:
        verbose_name_plural = "Detalles de venta"

class Pago(models.Model):
    """
    Representa un pago asociado a una venta.
    """
    METODOS = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('SALDO', 'Saldo prepago'),
        ('OTRO', 'Otro'),
    ]
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='pagos')
    metodo = models.CharField(max_length=20, choices=METODOS)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    tasa = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # porcentaje aplicado
    monto_final = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # monto con tasa aplicada
    observacion = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.monto <= 0:
            raise ValueError("El monto debe ser mayor a cero.")
        if self.metodo not in dict(self.METODOS):
            raise ValueError("Método de pago inválido.")
        # Validación: no permitir pagar más que el total de la venta
        total_pagado = sum(p.monto for p in self.venta.pagos.exclude(pk=self.pk))
        if self.monto + total_pagado > self.venta.total:
            raise ValueError("El monto de pago excede el total de la venta.")
        # Tasas
        if self.metodo == 'TARJETA_CREDITO':
            self.tasa = Decimal('5.0')
        elif self.metodo == 'TARJETA_DEBITO':
            self.tasa = Decimal('2.0')
        else:
            self.tasa = Decimal('0.0')
        self.monto_final = self.monto + (self.monto * self.tasa / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.metodo} - {self.monto} Gs. ({self.fecha:%d/%m/%Y})"

    class Meta:
        ordering = ['-fecha']
        verbose_name_plural = "Pagos"

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
