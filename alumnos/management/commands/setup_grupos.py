from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

class Command(BaseCommand):
    help = 'Crea los grupos y permisos necesarios para el sistema'

    def handle(self, *args, **options):
        self.stdout.write('Creando grupos y permisos...')
        
        # Obtener configuración de grupos desde settings
        grupos_config = getattr(settings, 'GRUPOS_SISTEMA', {})
        
        for grupo_nombre, config in grupos_config.items():
            # Crear o obtener el grupo
            grupo, created = Group.objects.get_or_create(name=grupo_nombre)
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Grupo "{grupo_nombre}" creado.')
                )
            else:
                self.stdout.write(f'Grupo "{grupo_nombre}" ya existe.')
            
            # Limpiar permisos existentes
            grupo.permissions.clear()
            
            # Asignar permisos
            permisos_asignados = 0
            for perm_codename in config.get('permissions', []):
                try:
                    app_label, codename = perm_codename.split('.')
                    permission = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename
                    )
                    grupo.permissions.add(permission)
                    permisos_asignados += 1
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Permiso "{perm_codename}" no encontrado.')
                    )
                except ValueError:
                    self.stdout.write(
                        self.style.ERROR(f'Formato de permiso inválido: "{perm_codename}"')
                    )
            
            self.stdout.write(
                f'Se asignaron {permisos_asignados} permisos al grupo "{grupo_nombre}".'
            )
        
        self.stdout.write(
            self.style.SUCCESS('Configuración de grupos completada.')
        )