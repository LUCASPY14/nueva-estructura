# productos/models.py
from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(
        max_length=100,
        blank=True,
        help_text="Datos de contacto (teléfono o email) del proveedor (opcional)."
    )

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    codigo = models.CharField(
        max_length=30,
        unique=True,
        help_text="Código interno o manual que identifica al producto"
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    cantidad = models.PositiveIntegerField(
        default=0,
        help_text="Stock disponible (unidades)"
    )
    precio_costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio de costo en Gs."
    )
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio de venta en Gs."
    )
    categoria = models.CharField(
        max_length=50,
        blank=True,
        help_text="Categoría (por ej. Bebidas, Snacks, etc.)"
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos',
        help_text="Proveedor de este producto"
    )

    def __str__(self):
        return f"{self.nombre} [{self.codigo}]"
