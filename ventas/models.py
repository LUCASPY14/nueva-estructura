from django.db import models
from django.conf import settings
from django.utils import timezone
from alumnos.models import Alumno
from productos.models import Producto

User = settings.AUTH_USER_MODEL

class AuthorizationCode(models.Model):
    """
    Código generado por un Admin que autoriza sobregiros.
    """
    code = models.CharField(max_length=20, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} {'(activo)' if self.is_active else '(inactivo)'}"


class Venta(models.Model):
    CONDICION_CHOICES = [
        ('CONTADO', 'Contado'),
        ('CREDITO', 'Crédito'),
    ]
    alumno = models.ForeignKey(Alumno, on_delete=models.PROTECT, related_name='ventas')
    cajero = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    condicion = models.CharField(max_length=10, choices=CONDICION_CHOICES, default='CONTADO')
    sobregiro_autorizado = models.BooleanField(default=False)
    codigo_autorizacion = models.ForeignKey(
        AuthorizationCode, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"Venta #{self.id} - {self.alumno.nombre} ({self.fecha:%d/%m/%Y %H:%M})"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    def subtotal(self):
        if self.cantidad is None or self.precio_unitario is None:
            return 0
        return self.cantidad * self.precio_unitario


class Pago(models.Model):
    METODO_CHOICES = [
        ('TARJETA_PREPAGO', 'Tarjeta Prepago'),
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('GIRO_TIGO', 'Giro Tigo'),
    ]
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='pagos')
    metodo = models.CharField(max_length=20, choices=METODO_CHOICES)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    transaccion = models.CharField(
        max_length=100,
        blank=True,
        help_text="Número de transacción (si aplica)"
    )

    def __str__(self):
        return f"{self.get_metodo_display()}: {self.monto}"
