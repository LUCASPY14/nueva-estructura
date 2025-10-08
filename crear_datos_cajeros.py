#!/usr/bin/env python
"""
Script para crear datos de ejemplo para el sistema de cajeros
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/ucas1/nueva_estructura')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgservice.settings')
django.setup()

from ventas.models import Caja, MetodoPago

def crear_datos_cajeros():
    print("\n🏪 CREANDO DATOS DE EJEMPLO PARA CAJEROS")
    print("="*50)
    
    # Crear cajas
    cajas_data = [
        {
            'numero': 1,
            'nombre': 'Caja Principal',
            'ubicacion': 'Entrada principal',
            'activa': True
        },
        {
            'numero': 2,
            'nombre': 'Caja Express',
            'ubicacion': 'Patio de comidas',
            'activa': True
        },
        {
            'numero': 3,
            'nombre': 'Caja Eventos',
            'ubicacion': 'Auditorio',
            'activa': False
        }
    ]
    
    print("📦 Creando cajas...")
    for caja_data in cajas_data:
        caja, created = Caja.objects.get_or_create(
            numero=caja_data['numero'],
            defaults=caja_data
        )
        status = "✅ Creada" if created else "ℹ️  Ya existe"
        print(f"   {status}: {caja.nombre}")
    
    # Crear métodos de pago si no existen
    metodos_pago = [
        {
            'nombre': 'Efectivo',
            'descripcion': 'Pago en efectivo',
            'activo': True,
            'requiere_referencia': False
        },
        {
            'nombre': 'Tarjeta Cantina',
            'descripcion': 'Saldo de tarjeta de cantina',
            'activo': True,
            'requiere_referencia': False
        },
        {
            'nombre': 'Transferencia',
            'descripcion': 'Transferencia bancaria',
            'activo': True,
            'requiere_referencia': True
        }
    ]
    
    print("\n💳 Creando métodos de pago...")
    for metodo_data in metodos_pago:
        metodo, created = MetodoPago.objects.get_or_create(
            nombre=metodo_data['nombre'],
            defaults=metodo_data
        )
        status = "✅ Creado" if created else "ℹ️  Ya existe"
        print(f"   {status}: {metodo.nombre}")
    
    print("\n📊 RESUMEN FINAL:")
    print("-" * 30)
    print(f"🏪 Total cajas: {Caja.objects.count()}")
    print(f"   Activas: {Caja.objects.filter(activa=True).count()}")
    print(f"💳 Métodos de pago: {MetodoPago.objects.count()}")
    print(f"   Activos: {MetodoPago.objects.filter(activo=True).count()}")
    
    print("\n✅ DATOS CREADOS EXITOSAMENTE!")
    print("Ahora el sistema de cajeros tiene:")
    print("• Cajas configuradas y listas para usar")
    print("• Métodos de pago disponibles")
    print("• Todo preparado para abrir turnos")

if __name__ == "__main__":
    crear_datos_cajeros()