from django.db import models

class ConfiguracionSistema(models.Model):
    """Modelo básico para pruebas"""
    clave = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'
    
    def __str__(self):
        return self.clave
