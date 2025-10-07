from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UsuarioLG
from alumnos.models import Padre

@receiver(post_save, sender=UsuarioLG)
def crear_padre_profile(sender, instance, created, **kwargs):
    if created and instance.tipo == 'PADRE':
        # Crear padre con los datos del usuario
        Padre.objects.create(
            nombre=instance.first_name or 'Sin nombre',
            apellido=instance.last_name or 'Sin apellido',
            email=instance.email
        )
