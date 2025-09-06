from django.db import models
from decimal import Decimal

class Proveedor(models.Model):
    """
    Representa a un proveedor de productos para la cantina.
    """
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100, blank=True)  # Contacto opcional

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = "Proveedores"

class Compra(models.Model):
    """
    Representa una compra de productos realizada a un proveedor.
    """
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def calcular_total(self):
        total = sum(detalle.subtotal() for detalle in self.detalles.all())
        self.total = total
        return total

    def save(self, *args, **kwargs):
        self.calcular_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor.nombre} - {self.fecha:%d/%m/%Y}"

    class Meta:
        ordering = ['-fecha']
        verbose_name_plural = "Compras"

class DetalleCompra(models.Model):
    """
    Detalle de productos comprados en una compra.
    """
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def subtotal(self):
        cantidad = self.cantidad or 0
        precio = self.precio_unitario or Decimal('0.00')
        return cantidad * precio

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad} a {self.precio_unitario} Gs."

    class Meta:
        verbose_name_plural = "Detalles de compra"
        ordering = ['compra', 'producto']
