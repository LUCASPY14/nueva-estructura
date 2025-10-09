#!/usr/bin/env python
"""
Script para demostrar el flujo completo de apertura de turno
y crear datos de prueba para el sistema de cajeros
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/ucas1/nueva_estructura')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgservice.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from ventas.models import TurnoCajero, Caja
from decimal import Decimal

User = get_user_model()

def abrir_turno_prueba():
    print("\n" + "="*60)
    print("🏪 DEMOSTRACION: APERTURA DE TURNO DE CAJA")
    print("="*60)
    
    # Buscar un cajero (usuario con tipo_usuario cajero)
    try:
        cajero = User.objects.filter(tipo_usuario='cajero').first()
        if not cajero:
            # Si no hay cajero, usar admin para la demo
            cajero = User.objects.filter(is_superuser=True).first()
            print(f"⚠️  No se encontró cajero, usando admin: {cajero.get_full_name()}")
        else:
            print(f"👤 Cajero seleccionado: {cajero.get_full_name()}")
    except Exception as e:
        print(f"❌ Error al buscar cajero: {e}")
        return
    
    # Verificar si ya hay un turno activo
    turno_existente = TurnoCajero.objects.filter(
        cajero=cajero,
        fecha_fin__isnull=True
    ).first()
    
    if turno_existente:
        print(f"ℹ️  Ya existe un turno activo desde: {turno_existente.fecha_inicio}")
        print(f"   Caja: {turno_existente.caja}")
        print(f"   Monto inicial: ${turno_existente.monto_inicial}")
        return turno_existente
    
    # Buscar caja disponible
    caja = Caja.objects.filter(activa=True).first()
    if not caja:
        print("❌ No hay cajas activas disponibles")
        return
    
    print(f"🏪 Caja seleccionada: {caja}")
    
    # Crear turno
    monto_inicial = Decimal('50000.00')  # $50,000 CLP
    
    turno = TurnoCajero.objects.create(
        cajero=cajero,
        caja=caja,
        monto_inicial=monto_inicial,
        observaciones_apertura='Turno de prueba - Demo del sistema'
    )
    
    print("\n✅ TURNO ABIERTO EXITOSAMENTE!")
    print("-" * 40)
    print(f"🆔 ID del turno: {turno.id}")
    print(f"👤 Cajero: {turno.cajero.get_full_name()}")
    print(f"🏪 Caja: {turno.caja}")
    print(f"⏰ Fecha/Hora inicio: {turno.fecha_inicio.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"💰 Monto inicial: ${turno.monto_inicial:,.0f} CLP")
    print(f"📝 Observaciones: {turno.observaciones_apertura}")
    
    print("\n🎯 ACCIONES DISPONIBLES AHORA:")
    print("-" * 40)
    print("✅ Acceso al POS (Punto de Venta)")
    print("✅ Realizar ventas")
    print("✅ Consultar saldos de alumnos")
    print("✅ Ver estadísticas en tiempo real")
    print("✅ Al final del día: Cerrar turno con arqueo")
    
    print("\n🌐 URLS ACTIVAS:")
    print("-" * 40)
    print("📊 Dashboard: http://localhost:8000/ventas/dashboard/")
    print("💰 POS: http://localhost:8000/ventas/pos/")
    print("📝 Nueva Venta: http://localhost:8000/ventas/nueva/")
    print("🔒 Cerrar Turno: http://localhost:8000/ventas/turno/cerrar/")
    
    return turno

def mostrar_estado_sistema():
    print("\n" + "="*60)
    print("📊 ESTADO ACTUAL DEL SISTEMA")
    print("="*60)
    
    # Turnos activos
    turnos_activos = TurnoCajero.objects.filter(fecha_fin__isnull=True)
    print(f"🔄 Turnos activos: {turnos_activos.count()}")
    
    for turno in turnos_activos:
        print(f"   • {turno.cajero.get_full_name()} en {turno.caja}")
        print(f"     Desde: {turno.fecha_inicio.strftime('%H:%M:%S')}")
        print(f"     Monto inicial: ${turno.monto_inicial:,.0f}")
    
    # Cajas disponibles
    cajas_activas = Caja.objects.filter(activa=True)
    print(f"\n🏪 Cajas activas: {cajas_activas.count()}")
    for caja in cajas_activas:
        turno_en_caja = TurnoCajero.objects.filter(
            caja=caja, 
            fecha_fin__isnull=True
        ).first()
        estado = "🔴 En uso" if turno_en_caja else "🟢 Disponible"
        print(f"   • {caja} - {estado}")
    
    # Estadísticas del día
    hoy = timezone.now().date()
    turnos_hoy = TurnoCajero.objects.filter(fecha_inicio__date=hoy)
    print(f"\n📅 Turnos abiertos hoy: {turnos_hoy.count()}")
    
    print("\n🚀 ¡SISTEMA LISTO PARA OPERAR!")

if __name__ == "__main__":
    turno = abrir_turno_prueba()
    if turno:
        mostrar_estado_sistema()
        
        print("\n" + "="*60)
        print("🎉 DEMO COMPLETADA - TURNO ACTIVO")
        print("="*60)
        print("Ahora puedes:")
        print("1️⃣  Ir al dashboard y ver el turno activo")
        print("2️⃣  Acceder al POS para realizar ventas")
        print("3️⃣  Probar todas las funcionalidades")
        print("4️⃣  Al final, cerrar el turno con arqueo")