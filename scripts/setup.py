#!/usr/bin/env python
"""
Script de configuración inicial del sistema de cantina
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n{'='*50}")
    print(f"🔧 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}:")
        print(f"Comando: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🏫 SISTEMA DE CANTINA - CONFIGURACIÓN INICIAL")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('manage.py'):
        print("❌ Error: No se encontró manage.py")
        print("   Ejecute este script desde el directorio raíz del proyecto")
        sys.exit(1)
    
    # Lista de comandos a ejecutar
    commands = [
        ("python manage.py makemigrations", "Creando migraciones"),
        ("python manage.py migrate", "Aplicando migraciones"),
        ("python manage.py setup_grupos", "Configurando grupos y permisos"),
        ("python manage.py setup_inicial --crear-admin", "Configuración inicial del sistema"),
        ("python manage.py collectstatic --noinput", "Recolectando archivos estáticos"),
    ]
    
    # Ejecutar comandos
    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
    
    # Resumen final
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN DE CONFIGURACIÓN")
    print(f"{'='*60}")
    print(f"✅ Comandos ejecutados exitosamente: {success_count}/{len(commands)}")
    
    if success_count == len(commands):
        print("\n🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
        print("\n📝 PRÓXIMOS PASOS:")
        print("   1. Inicie el servidor: python manage.py runserver")
        print("   2. Acceda al admin: http://127.0.0.1:8000/admin/")
        print("   3. Usuario: admin | Contraseña: admin123")
        print("   4. ¡CAMBIE LA CONTRASEÑA INMEDIATAMENTE!")
        print("\n🔗 URLs importantes:")
        print("   - Admin: http://127.0.0.1:8000/admin/")
        print("   - Dashboard: http://127.0.0.1:8000/")
        print("   - Alumnos: http://127.0.0.1:8000/alumnos/")
    else:
        print(f"\n⚠️  Se completaron {success_count} de {len(commands)} pasos")
        print("   Revise los errores y ejecute manualmente los comandos fallidos")

if __name__ == "__main__":
    main()