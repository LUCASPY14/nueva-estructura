from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    # ...otros campos que tengas en productos...

    def __str__(self):
        return self.nombre

class MovimientoStock(models.Model):
    ENTRADA = 'entrada'
    SALIDA = 'salida'
    TIPO_CHOICES = [
        (ENTRADA, 'Entrada'),
        (SALIDA, 'Salida'),
    ]

    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    referencia = models.CharField(max_length=255, blank=True, help_text='Ejemplo: Compra, Venta, Ajuste, etc.')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto} - {self.tipo} ({self.cantidad})"

    class Meta:
        verbose_name = "Movimiento de stock"
        verbose_name_plural = "Movimientos de stock"
