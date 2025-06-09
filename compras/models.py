# compras/models.py
from django.db import models
from django.utils import timezone
from productos.models import Producto, Proveedor

class Compra(models.Model):
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='compras',
        help_text="Proveedor al que se le realiza la compra"
    )
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Suma de subtotales de los detalles"
    )

    def __str__(self):
        return f"Compra #{self.id} a {self.proveedor.nombre} ({self.fecha.strftime('%d/%m/%Y')})"

    def calcular_total(self):
        """
        Recalcula el total sumando los subtotales de todos los detalles asociados.
        """
        total = sum(item.subtotal() for item in self.detalles.all())
        self.total = total
        return total

class DetalleCompra(models.Model):
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_compra'
    )
    cantidad = models.PositiveIntegerField(
        help_text="Cantidad de unidades compradas"
    )
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Precio de costo por unidad en Gs."
    )

    def __str__(self):
        return f"{self.cantidad}×{self.producto.nombre} @ {self.precio_unitario}"

    def subtotal(self):
        if self.cantidad is None or self.precio_unitario is None:
            return 0
        return self.cantidad * self.precio_unitario