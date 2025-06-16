# listar_modelos.py
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lgservice.settings")  # Cambia por tu settings.py
django.setup()

from django.apps import apps

print("\n----- MODELOS Y RELACIONES DEL PROYECTO -----\n")

for app_config in apps.get_app_configs():
    print(f"\nApp: {app_config.label}")
    for model in app_config.get_models():
        print(f"  Modelo: {model.__name__}")
        for field in model._meta.get_fields():
            if field.is_relation:
                print(f"    - Relación: {field.name} → {field.related_model} (tipo: {field.get_internal_type()})")
print("\n----- FIN DEL LISTADO -----\n")
