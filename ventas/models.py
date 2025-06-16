from django.db import models
from decimal import Decimal
from alumnos.models import Alumno
from productos.models import Producto

class Venta(models.Model):
    CONDICIONES = [
    ('CONTADO', 'Contado'),
    ('CREDITO', 'Crédito'),
]
    condicion = models.CharField(max_length=10, choices=CONDICIONES, default='CONTADO')
    """
    Representa una venta realizada a un alumno.
    """
    alumno = models.ForeignKey(Alumno, on_delete=models.PROTECT, related_name='ventas')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    # Para expansión: cajero = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def calcular_total(self):
        """
        Calcula y actualiza el total de la venta sumando los subtotales de los detalles.
        """
        total = sum(detalle.subtotal() for detalle in self.detalles.all())
        self.total = total
        return total

    def __str__(self):
        return f"Venta #{self.id} - {self.alumno.nombre} - {self.fecha:%d/%m/%Y}"

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

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

class Pago(models.Model):
    METODOS = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('SALDO', 'Saldo prepago'),
        ('OTRO', 'Otro'),
    ]
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='pagos')
    metodo = models.CharField(max_length=15, choices=METODOS, default='EFECTIVO')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.metodo} - {self.monto} Gs. ({self.fecha:%d/%m/%Y})"

class AuthorizationCode(models.Model):
    codigo = models.CharField(max_length=32, unique=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='autorizaciones')
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)  # opcional

    def __str__(self):
        return f"{self.codigo} - {self.venta} ({self.fecha})"
