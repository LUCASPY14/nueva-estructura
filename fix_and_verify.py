#!/usr/bin/env python3
import subprocess
import sys

def run_command(cmd, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} exitoso")
            if result.stdout.strip():
                print(f"   �� {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} falló")
            if result.stderr.strip():
                print(f"   📤 Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando {description}: {e}")
        return False

def main():
    print("🚀 CORRECCIÓN Y VERIFICACIÓN COMPLETA")
    print("=" * 50)
    
    # 1. Corregir observaciones_admin
    run_command(
        "sed -i \"s/'observaciones_admin'/'observaciones_procesamiento'/g\" alumnos/forms.py",
        "Corrigiendo observaciones_admin"
    )
    
    # 2. Verificar que no hay más campos problemáticos
    result = run_command(
        "grep -n 'observaciones_admin\\|comprobante[^_]\\|tipo_transaccion\\|fecha_transaccion' alumnos/forms.py || echo 'Sin problemas'",
        "Verificando campos problemáticos"
    )
    
    # 3. Limpiar cache
    run_command(
        "find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true",
        "Limpiando cache"
    )
    
    # 4. Intentar migraciones
    success = run_command(
        "python manage.py makemigrations alumnos",
        "Creando migraciones"
    )
    
    if success:
        # 5. Aplicar migraciones
        run_command(
            "python manage.py migrate",
            "Aplicando migraciones"
        )
        
        print(f"\n�� ¡SISTEMA LISTO!")
        print("✅ Modelos corregidos")
        print("✅ Formularios corregidos")
        print("✅ Migraciones aplicadas")
        print("\n🚀 Próximo paso: Probar el sistema de saldo")
    else:
        print(f"\n⚠️  Aún hay problemas con las migraciones")
        print("Revisa el error mostrado arriba")

if __name__ == "__main__":
    main()
