from django.db import models
from django.utils import timezone
from productos.models import Producto

class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso'),
    ]
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='movimientos'
    )
    tipo = models.CharField(
        max_length=7,
        choices=TIPO_CHOICES
    )
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(default=timezone.now)
    motivo = models.CharField(
        max_length=200,
        blank=True,
        help_text="Descripción del motivo (p.ej. ajuste, pérdida, etc.)"
    )
    referencia = models.CharField(
        max_length=50,
        blank=True,
        help_text="ID de Compra/Venta u otra referencia opcional"
    )

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.cantidad} en {self.producto.nombre}"

    def aplicar(self):
        """
        Ajusta el stock del producto según el movimiento.
        """
        if self.tipo == 'INGRESO':
            self.producto.cantidad += self.cantidad
        else:
            self.producto.cantidad -= self.cantidad
        self.producto.save()