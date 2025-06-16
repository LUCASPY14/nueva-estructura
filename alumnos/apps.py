from django.apps import AppConfig

class AlumnosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alumnos'
    verbose_name = "Gestión de Alumnos"
    # def ready(self):
    #     import alumnos.signals
