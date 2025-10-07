from django.apps import AppConfig

class VentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ventas'
    
    # No importar modelos aquí
    
    def ready(self):
        # Importaciones solo dentro de ready
        pass