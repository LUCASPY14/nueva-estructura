from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class UsuarioLG(AbstractUser):
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

    groups = models.ManyToManyField(
        Group,
        verbose_name='grupos',
        blank=True,
        related_name='usuarioslg_set',         # evita choque con auth.User.groups
        related_query_name='usuario_lg'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='permisos de usuario',
        blank=True,
        related_name='usuarioslg_permissions',  # evita choque con auth.User.user_permissions
        related_query_name='usuario_lg_perm'
    )
