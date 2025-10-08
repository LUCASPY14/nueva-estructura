from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Modelo de usuario para la Cantina de Tita"""
    
    TIPO_USUARIO_CHOICES = [
        ('administrador', '👑 Administrador'),
        ('cajero', '💰 Cajero'),
        ('padre', '👨‍👩‍👧‍👦 Padre/Tutor'),
        ('supervisor', '👨‍💼 Supervisor'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=20, 
        choices=TIPO_USUARIO_CHOICES, 
        default='cajero',
        verbose_name='Tipo de Usuario'
    )
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Usuario - Cantina de Tita'
        verbose_name_plural = 'Usuarios - Cantina de Tita'
        db_table = 'usuarios_customuser'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_tipo_usuario_display()})"
    
    @property
    def es_administrador(self):
        return self.tipo_usuario == 'administrador' or self.is_superuser
    
    @property
    def es_cajero(self):
        return self.tipo_usuario == 'cajero'
    
    @property
    def es_padre(self):
        return self.tipo_usuario == 'padre'
    
    @property
    def es_supervisor(self):
        return self.tipo_usuario == 'supervisor'
