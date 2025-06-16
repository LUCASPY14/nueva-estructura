from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UsuarioLG
from alumnos.models import Padre

@receiver(post_save, sender=UsuarioLG)
def crear_padre_profile(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil de Padre cuando se crea un usuario de tipo 'PADRE'.
    """
    if created and instance.tipo == 'PADRE':
        Padre.objects.create(usuario=instance)
        # print(f"Perfil de Padre creado para el usuario {instance.username}")
