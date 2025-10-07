#!/usr/bin/env python
"""
Script para configurar datos de prueba del sistema LG Service
"""
import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgservice.settings')
django.setup()

from django.db import transaction
from usuarios.models import UsuarioLG
from alumnos.models import Curso, Alumno, Transaccion

def main():
    print("🚀 Configurando datos de prueba para LG Service...")
    
    with transaction.atomic():
        try:
            # 1. Crear usuario administrador
            print("\n👨‍💼 Creando usuario administrador...")
            admin_user, created = UsuarioLG.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@colegio.com',
                    'first_name': 'Administrador',
                    'last_name': 'Sistema',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True
                }
            )
            
            if created:
                admin_user.set_password('admin123')
                admin_user.save()
                print(f"   ✅ Usuario admin creado: admin/admin123")
            else:
                print(f"   ✓ Usuario admin ya existe")
            
            # 2. Crear cursos si no existen
            print("\n📚 Verificando cursos...")
            cursos_nombres = [
                "1° Básico", "2° Básico", "3° Básico", "4° Básico",
                "5° Básico", "6° Básico", "7° Básico", "8° Básico"
            ]
            
            for nombre in cursos_nombres:
                curso, created = Curso.objects.get_or_create(nombre=nombre)
                if created:
                    print(f"   ✅ Curso creado: {nombre}")
            
            # 3. Verificar alumnos existentes
            print("\n🎓 Verificando alumnos...")
            alumnos = Alumno.objects.all()
            print(f"   📊 Total alumnos: {alumnos.count()}")
            
            if alumnos.count() == 0:
                print("   ℹ️ No hay alumnos. Cree algunos desde el panel admin.")
                print("   🔗 http://127.0.0.1:8000/admin/alumnos/alumno/add/")
            else:
                # 4. Asignar saldo inicial a alumnos sin saldo
                print("\n💰 Asignando saldo inicial...")
                alumnos_sin_saldo = alumnos.filter(saldo_tarjeta=0)
                
                for alumno in alumnos_sin_saldo[:5]:  # Primeros 5 alumnos
                    monto_inicial = Decimal('20000')  # $20.000 inicial
                    
                    # Actualizar saldo
                    alumno.saldo_tarjeta = monto_inicial
                    alumno.save()
                    
                    # Crear transacción
                    Transaccion.objects.create(
                        alumno=alumno,
                        tipo='recarga',
                        monto=monto_inicial,
                        saldo_anterior=Decimal('0'),
                        saldo_posterior=monto_inicial,
                        usuario_responsable=admin_user,
                        descripcion='Saldo inicial de prueba'
                    )
                    
                    print(f"   ✅ ${monto_inicial} asignado a {alumno.get_nombre_completo()}")
            
            # 5. Mostrar resumen final
            print("\n📋 RESUMEN FINAL:")
            print(f"   👨‍💼 Usuarios: {UsuarioLG.objects.count()}")
            print(f"   📚 Cursos: {Curso.objects.count()}")
            print(f"   🎓 Alumnos: {Alumno.objects.count()}")
            print(f"   💰 Transacciones: {Transaccion.objects.count()}")
            
            # 6. Mostrar saldos actuales
            print("\n💳 SALDOS ACTUALES:")
            for alumno in Alumno.objects.all()[:10]:  # Primeros 10
                print(f"   🎓 {alumno.get_nombre_completo()}: ${alumno.saldo_tarjeta}")
            
            # 7. Mostrar URLs importantes
            print("\n🔗 URLS IMPORTANTES:")
            print("   🏠 Inicio: http://127.0.0.1:8000/")
            print("   🎓 Alumnos: http://127.0.0.1:8000/alumnos/")
            print("   🔧 Admin: http://127.0.0.1:8000/admin/")
            print("   👨‍💼 Login Admin: admin / admin123")
            
            print("\n🎉 ¡Configuración completada exitosamente!")
            
        except Exception as e:
            print(f"❌ Error durante la configuración: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
