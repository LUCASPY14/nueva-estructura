from django.db import models
from django.utils import timezone
from ventas.models import Venta

class Factura(models.Model):
    """
    Representa una factura electrónica generada a partir de una venta.
    """
    venta = models.OneToOneField(
        Venta,
        on_delete=models.CASCADE,
        related_name='factura'
    )
    numero = models.CharField(
        max_length=20,
        unique=True,
        help_text="Número de factura único. Puede incluir prefijo."
    )
    fecha_emision = models.DateTimeField(default=timezone.now)
    ruc = models.CharField(max_length=20, blank=True, null=True)
    razon_social = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Factura #{self.numero} - {self.venta.alumno.nombre} - {self.total} Gs."

    class Meta:
        ordering = ['-fecha_emision']
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
