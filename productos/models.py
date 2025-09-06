from django.db import models
from decimal import Decimal
from proveedores.models import Proveedor

class Categoria(models.Model):
    """
    Categoría a la que pertenece un producto (bebidas, snacks, etc.).
    """
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    """
    Representa un producto disponible para la venta en la cantina.
    """
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    cantidad = models.PositiveIntegerField(default=0)
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)

    def stock_actual(self):
        """
        Calcula el stock actual en base a movimientos registrados.
        Requiere relación inversa 'movimientos' desde MovimientoStock.
        """
        total = self.movimientos.aggregate(total=models.Sum('cantidad'))['total'] or 0
        return Decimal(total)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    class Meta:
        ordering = ['nombre']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
