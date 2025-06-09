from django.db import models
from django.conf import settings
from decimal import Decimal
from productos.models import Producto
from datetime import date

Usuario = settings.AUTH_USER_MODEL

class Padre(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='padre_profile'
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    razon_social = models.CharField(
        max_length=150,
        blank=True,
        help_text="Razón social (si aplica). Dejar vacío si no corresponde."
    )
    ruc = models.CharField(
        max_length=20,
        blank=True,
        help_text="RUC para facturación (si corresponde)."
    )
    email = models.EmailField(
        max_length=254,
        help_text="Correo para envío de factura electrónica."
    )
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    barrio = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Alumno(models.Model):
    padre = models.ForeignKey(
        Padre,
        on_delete=models.CASCADE,
        related_name='alumnos'
    )
    nombre = models.CharField(max_length=100)
    grado = models.CharField(max_length=50, blank=True)
    nivel = models.CharField(max_length=50, blank=True)
    limite_consumo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Monto máximo que el alumno puede gastar por día"
    )
    saldo_tarjeta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Saldo cargado en la tarjeta prepaga (uso exclusivo Cantina)"
    )
    numero_tarjeta = models.CharField(
        max_length=20,
        blank=True, null=True,
        help_text="Número de tarjeta (uso exclusivo de La Cantina de Tita)."
    )

    def __str__(self):
        return f"{self.nombre} (Tarjeta: {self.numero_tarjeta})"

    def total_consumido(self, fecha=None):
        """
        Retorna el total consumido por el alumno.
        Si se pasa una fecha, filtra las ventas de ese día.
        """
        ventas = self.ventas.all()  # asumiendo related_name='ventas' en Venta.alumno
        if fecha:
            ventas = ventas.filter(fecha=fecha)
        return sum(v.total for v in ventas)

    def saldo_restante(self, fecha=None):
        """
        Retorna el saldo restante considerando el límite de consumo diario.
        Si se pasa una fecha, descuenta lo consumido ese día.
        """
        if fecha:
            consumido = self.total_consumido(fecha=fecha)
            restante = min(self.saldo_tarjeta, self.limite_consumo - consumido)
            return max(Decimal('0.00'), restante)
        return self.saldo_tarjeta

    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"

class Restriccion(models.Model):
    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.CASCADE,
        related_name='restricciones'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='restricciones_por_alumno'
    )
    permitido = models.BooleanField(
        default=True,
        help_text="True=puede comprar, False=no puede"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['alumno', 'producto'], name='unique_restriccion_alumno_producto')
        ]
        verbose_name = "Restricción"
        verbose_name_plural = "Restricciones"

    def __str__(self):
        estado = "Permitido" if self.permitido else "Prohibido"
        return f"{self.alumno.nombre} → {self.producto.nombre}: {estado}"
    
    def total_consumido(self, fecha=None): """ Retorna el total consumido por el alumno.
                Si se pasa una fecha, filtra las ventas de ese mes. """
    Ventas = self.ventas.all()
    if fecha:
                ventas = ventas.filter(fecha__year=fecha.year, fecha__month=fecha.month)
            return sum(v.total for v in ventas)