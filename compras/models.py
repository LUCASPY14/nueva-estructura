from django.db import models
from django.utils import timezone
from proveedores.models import Proveedor  # Importar el modelo desde la app correcta

class Compra(models.Model):
    """
    Representa una compra realizada a un proveedor.
    """
    numero_factura = models.CharField(
        max_length=50, 
        unique=True, 
        default='PENDIENTE',  # Agregar valor por defecto
        help_text="Número de factura del proveedor"
    )
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='compras')
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagada = models.BooleanField(default=False)
    notas = models.TextField(blank=True)
    
    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor.nombre}"
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = "Compra"
        verbose_name_plural = "Compras"

class DetalleCompra(models.Model):
    """
    Representa un ítem individual en una compra.
    """
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} x ${self.precio_unitario}"
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
