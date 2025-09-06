from django.db import models

class ConfiguracionSistema(models.Model):
    nombre_sistema = models.CharField(max_length=100, default="LGservice")
    moneda = models.CharField(max_length=10, default="Gs.")
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    horario_atencion = models.CharField(max_length=100, default="07:00 a 17:00")
    color_principal = models.CharField(max_length=20, default="#16a34a")
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)

    def __str__(self):
        return "Configuración del Sistema"