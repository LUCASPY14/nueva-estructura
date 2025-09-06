from django.db import models

class MovimientoStock(models.Model):
    """
    Registra los movimientos de stock (entradas y salidas) de un producto.
    """
    ENTRADA = 'entrada'
    SALIDA = 'salida'

    TIPO_CHOICES = [
        (ENTRADA, 'Entrada'),
        (SALIDA, 'Salida'),
    ]

    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.CASCADE,
        related_name='movimientos'
    )
    cantidad = models.PositiveIntegerField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    referencia = models.CharField(
        max_length=255,
        blank=True,
        help_text='Ejemplo: Compra, Venta, Ajuste, etc.'
    )
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.tipo} ({self.cantidad}) - {self.fecha:%d/%m/%Y}"

    @property
    def es_entrada(self):
        return self.tipo == self.ENTRADA

    @property
    def es_salida(self):
        return self.tipo == self.SALIDA

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Movimiento de stock"
        verbose_name_plural = "Movimientos de stock"
