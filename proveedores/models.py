from django.db import models
from django.utils import timezone

class Proveedor(models.Model):
    """
    Representa un proveedor de productos para el negocio.
    """
    TIPOS_DOCUMENTO = [
        ('ruc', 'RUC'),
        ('dni', 'DNI'),
        ('ce', 'Carnet de Extranjería'),
        ('otro', 'Otro'),
    ]
    
    # Información básica
    nombre = models.CharField(max_length=100, db_index=True)
    nombre_comercial = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    tipo_documento = models.CharField(max_length=10, choices=TIPOS_DOCUMENTO, default='ruc')
    numero_documento = models.CharField(max_length=20, unique=True, db_index=True)
    
    # Contacto
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    telefono_alternativo = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True)
    
    # Persona de contacto
    contacto_nombre = models.CharField(max_length=100, blank=True, null=True)
    contacto_telefono = models.CharField(max_length=20, blank=True, null=True)
    contacto_email = models.EmailField(blank=True, null=True)
    
    # Información adicional
    rubro = models.CharField(max_length=100, blank=True, null=True)
    condiciones_pago = models.TextField(blank=True, null=True)
    tiempo_entrega_promedio = models.PositiveIntegerField(
        help_text="Tiempo promedio de entrega en días",
        null=True,
        blank=True
    )
    notas = models.TextField(blank=True, null=True)
    
    # Control
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)
    ultima_compra = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']
