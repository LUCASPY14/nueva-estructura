from django.db import models

class Proveedor(models.Model):
    """
    Representa un proveedor de productos para la cantina.
    """
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
