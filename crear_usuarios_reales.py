#!/usr/bin/env python
"""
Script para crear usuarios reales del sistema Cantina de Tita
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/home/ucas1/nueva_estructura')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgservice.settings')
django.setup()

from usuarios.models import CustomUser
from django.db import transaction

def crear_usuarios_reales():
    """Crear usuarios reales para el sistema Cantina de Tita"""
    print("🏫 Creando usuarios reales para Cantina de Tita...")
    
    usuarios_data = [
        # ADMINISTRADORES
        {
            'username': 'maria_rodriguez',
            'email': 'maria.rodriguez@cantinatita.com',
            'first_name': 'María',
            'last_name': 'Rodríguez',
            'tipo_usuario': 'administrador',
            'password': 'cantina2025*',
            'is_superuser': True,
            'is_staff': True,
            'descripcion': 'Directora General de Cantina de Tita'
        },
        {
            'username': 'carlos_sanchez',
            'email': 'carlos.sanchez@cantinatita.com',
            'first_name': 'Carlos',
            'last_name': 'Sánchez',
            'tipo_usuario': 'administrador',
            'password': 'admin2025*',
            'is_superuser': True,
            'is_staff': True,
            'descripcion': 'Administrador de Sistemas'
        },
        
        # CAJEROS
        {
            'username': 'ana_lopez',
            'email': 'ana.lopez@cantinatita.com',
            'first_name': 'Ana',
            'last_name': 'López',
            'tipo_usuario': 'cajero',
            'password': 'cajero123*',
            'descripcion': 'Cajera Turno Mañana'
        },
        {
            'username': 'pedro_gomez',
            'email': 'pedro.gomez@cantinatita.com',
            'first_name': 'Pedro',
            'last_name': 'Gómez',
            'tipo_usuario': 'cajero',
            'password': 'cajero456*',
            'descripcion': 'Cajero Turno Tarde'
        },
        {
            'username': 'lucia_martinez',
            'email': 'lucia.martinez@cantinatita.com',
            'first_name': 'Lucía',
            'last_name': 'Martínez',
            'tipo_usuario': 'cajero',
            'password': 'cajero789*',
            'descripcion': 'Cajera de Apoyo'
        },
        
        # SUPERVISORES
        {
            'username': 'jorge_hernandez',
            'email': 'jorge.hernandez@cantinatita.com',
            'first_name': 'Jorge',
            'last_name': 'Hernández',
            'tipo_usuario': 'supervisor',
            'password': 'supervisor123*',
            'is_staff': True,
            'descripcion': 'Supervisor de Operaciones'
        },
        {
            'username': 'sofia_torres',
            'email': 'sofia.torres@cantinatita.com',
            'first_name': 'Sofía',
            'last_name': 'Torres',
            'tipo_usuario': 'supervisor',
            'password': 'supervisor456*',
            'is_staff': True,
            'descripcion': 'Supervisora de Calidad'
        },
        
        # PADRES DE FAMILIA
        {
            'username': 'roberto_silva',
            'email': 'roberto.silva@gmail.com',
            'first_name': 'Roberto',
            'last_name': 'Silva',
            'tipo_usuario': 'padre',
            'password': 'padre123*',
            'descripcion': 'Padre de Familia - Hijo: Roberto Silva Jr. (3°A)'
        },
        {
            'username': 'patricia_morales',
            'email': 'patricia.morales@hotmail.com',
            'first_name': 'Patricia',
            'last_name': 'Morales',
            'tipo_usuario': 'padre',
            'password': 'madre123*',
            'descripcion': 'Madre de Familia - Hija: Isabella Morales (2°B)'
        },
        {
            'username': 'fernando_castro',
            'email': 'fernando.castro@yahoo.com',
            'first_name': 'Fernando',
            'last_name': 'Castro',
            'tipo_usuario': 'padre',
            'password': 'padre456*',
            'descripcion': 'Padre de Familia - Hijos: Fernando Jr. (4°A), Carmen Castro (1°C)'
        },
        {
            'username': 'elena_jimenez',
            'email': 'elena.jimenez@gmail.com',
            'first_name': 'Elena',
            'last_name': 'Jiménez',
            'tipo_usuario': 'padre',
            'password': 'madre456*',
            'descripcion': 'Madre de Familia - Hijo: Miguel Jiménez (5°A)'
        },
        {
            'username': 'diego_vargas',
            'email': 'diego.vargas@outlook.com',
            'first_name': 'Diego',
            'last_name': 'Vargas',
            'tipo_usuario': 'padre',
            'password': 'padre789*',
            'descripcion': 'Padre de Familia - Hija: Valentina Vargas (3°B)'
        }
    ]
    
    with transaction.atomic():
        creados = 0
        actualizados = 0
        
        for user_data in usuarios_data:
            username = user_data['username']
            
            # Verificar si el usuario ya existe
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'tipo_usuario': user_data['tipo_usuario'],
                    'is_superuser': user_data.get('is_superuser', False),
                    'is_staff': user_data.get('is_staff', False),
                    'is_active': True,
                }
            )
            
            # Establecer la contraseña
            user.set_password(user_data['password'])
            
            # Actualizar campos si es necesario
            if not created:
                user.email = user_data['email']
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.tipo_usuario = user_data['tipo_usuario']
                user.is_superuser = user_data.get('is_superuser', False)
                user.is_staff = user_data.get('is_staff', False)
                actualizados += 1
            else:
                creados += 1
            
            user.save()
            
            status = "✅ CREADO" if created else "🔄 ACTUALIZADO"
            tipo_emoji = {
                'administrador': '👑',
                'cajero': '💰',  
                'supervisor': '👁️',
                'padre': '👨‍👩‍👧‍👦'
            }.get(user_data['tipo_usuario'], '👤')
            
            print(f"   {status} {tipo_emoji} {user_data['first_name']} {user_data['last_name']} ({username})")
            print(f"      Tipo: {user_data['tipo_usuario']}")
            print(f"      Email: {user_data['email']}")
            print(f"      Descripción: {user_data['descripcion']}")
            print()
    
    print(f"📊 Resumen:")
    print(f"   ✅ Usuarios creados: {creados}")
    print(f"   🔄 Usuarios actualizados: {actualizados}")
    print(f"   📋 Total usuarios procesados: {len(usuarios_data)}")
    
    # Mostrar estadísticas por tipo
    stats = CustomUser.objects.values('tipo_usuario').annotate(
        count=models.Count('tipo_usuario')
    )
    
    print(f"\n📈 Estadísticas por tipo de usuario:")
    for stat in stats:
        tipo_emoji = {
            'administrador': '👑',
            'cajero': '💰',  
            'supervisor': '👁️',
            'padre': '👨‍👩‍👧‍👦'
        }.get(stat['tipo_usuario'], '👤')
        print(f"   {tipo_emoji} {stat['tipo_usuario'].title()}: {stat['count']} usuarios")

if __name__ == '__main__':
    from django.db import models
    crear_usuarios_reales()
    print("\n🎉 ¡Usuarios reales creados exitosamente para Cantina de Tita!")