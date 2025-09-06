from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class UsuarioLG(AbstractUser):
    """
    Usuario personalizado para LGservice.
    Roles soportados:
      - ADMIN: Administrador general del sistema.
      - CAJERO: Encargado de registrar ventas y cargar saldo.
      - PADRE: Responsable de uno o más alumnos.
    """

    ROLES = [
        ('ADMIN', 'Administrador'),
        ('CAJERO', 'Cajero'),
        ('PADRE', 'Padre'),
    ]

    tipo = models.CharField(max_length=7, choices=ROLES)

    def is_admin(self):
        return self.tipo == 'ADMIN'

    def is_cajero(self):
        return self.tipo == 'CAJERO'

    def is_padre(self):
        return self.tipo == 'PADRE'

    def get_rol_display(self):
        return dict(self.ROLES).get(self.tipo, 'Desconocido')

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

    # Campos redefinidos para evitar conflictos con AbstractUser
    groups = models.ManyToManyField(
        Group,
        verbose_name='grupos',
        blank=True,
        related_name='usuarioslg_set',
        related_query_name='usuario_lg'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='permisos de usuario',
        blank=True,
        related_name='usuarioslg_permissions',
        related_query_name='usuario_lg_perm'
    )

    class Meta:
        ordering = ['username']
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
