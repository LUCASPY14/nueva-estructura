# setup_metodos_pago.py
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgservice.settings')
django.setup()

from ventas.models import MetodoPago

def crear_metodos_pago():
    """
    Crear métodos de pago según especificación:
    - Tarjeta de cantina: genera recibo interno
    - Otros métodos: generan factura legal
    """
    
    metodos = [
        # Tarjetas de cantina (requieren recibo interno)
        {
            'nombre': 'Tarjeta Cantina Estudiantil',
            'descripcion': 'Tarjeta prepagada para estudiantes',
            'es_tarjeta_cantina': True,
            'requiere_referencia': True,
            'activo': True
        },
        {
            'nombre': 'Tarjeta Cantina Docente',
            'descripcion': 'Tarjeta prepagada para docentes',
            'es_tarjeta_cantina': True,
            'requiere_referencia': True,
            'activo': True
        },
        {
            'nombre': 'Tarjeta Cantina Personal',
            'descripcion': 'Tarjeta prepagada para personal administrativo',
            'es_tarjeta_cantina': True,
            'requiere_referencia': True,
            'activo': True
        },
        
        # Métodos que requieren facturación legal
        {
            'nombre': 'Efectivo',
            'descripcion': 'Pago en efectivo',
            'es_tarjeta_cantina': False,
            'requiere_referencia': False,
            'activo': True
        },
        {
            'nombre': 'Tarjeta de Crédito',
            'descripcion': 'Pago con tarjeta de crédito',
            'es_tarjeta_cantina': False,
            'requiere_referencia': True,
            'activo': True
        },
        {
            'nombre': 'Tarjeta de Débito',
            'descripcion': 'Pago con tarjeta de débito',
            'es_tarjeta_cantina': False,
            'requiere_referencia': True,
            'activo': True
        },
        {
            'nombre': 'Transferencia Bancaria',
            'descripcion': 'Pago por transferencia bancaria',
            'es_tarjeta_cantina': False,
            'requiere_referencia': True,
            'activo': True
        },
        {
            'nombre': 'Yape',
            'descripcion': 'Pago mediante aplicación Yape',
            'es_tarjeta_cantina': False,
            'requiere_referencia': True,
            'activo': True
        },
        {
            'nombre': 'Plin',
            'descripcion': 'Pago mediante aplicación Plin',
            'es_tarjeta_cantina': False,
            'requiere_referencia': True,
            'activo': True
        },
        {
            'nombre': 'POS',
            'descripcion': 'Pago con terminal POS',
            'es_tarjeta_cantina': False,
            'requiere_referencia': True,
            'activo': True
        }
    ]
    
    print("Creando métodos de pago...")
    
    for metodo_data in metodos:
        metodo, created = MetodoPago.objects.get_or_create(
            nombre=metodo_data['nombre'],
            defaults=metodo_data
        )
        
        if created:
            print(f"✓ Creado: {metodo.nombre}")
        else:
            print(f"- Ya existe: {metodo.nombre}")
    
    print("\n--- Resumen de métodos de pago ---")
    print("Tarjetas de cantina (recibo interno):")
    for metodo in MetodoPago.objects.filter(es_tarjeta_cantina=True):
        print(f"  • {metodo.nombre}")
    
    print("\nOtros métodos (factura legal):")
    for metodo in MetodoPago.objects.filter(es_tarjeta_cantina=False):
        print(f"  • {metodo.nombre}")
    
    print(f"\nTotal métodos creados: {MetodoPago.objects.count()}")

if __name__ == '__main__':
    crear_metodos_pago()