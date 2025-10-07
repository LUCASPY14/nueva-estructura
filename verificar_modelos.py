"""
Script para verificar qué modelos existen actualmente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgservice.settings')
django.setup()

def verificar_modelos_existentes():
    """Verifica qué modelos están definidos en alumnos"""
    print("🔍 VERIFICANDO MODELOS EXISTENTES EN ALUMNOS")
    print("=" * 50)
    
    try:
        # Importar todos los modelos disponibles
        from alumnos import models
        from django.db import models as django_models
        
        # Obtener todas las clases que son modelos de Django
        modelo_classes = []
        for name in dir(models):
            obj = getattr(models, name)
            if (isinstance(obj, type) and 
                issubclass(obj, django_models.Model) and 
                obj._meta.app_label == 'alumnos'):
                modelo_classes.append(obj)
        
        print(f"📋 Modelos encontrados: {len(modelo_classes)}")
        
        for modelo in modelo_classes:
            print(f"\n✅ {modelo.__name__}")
            print(f"   📄 Tabla: {modelo._meta.db_table}")
            
            # Mostrar campos principales
            campos = [f.name for f in modelo._meta.fields]
            print(f"   🔧 Campos ({len(campos)}): {', '.join(campos[:5])}{'...' if len(campos) > 5 else ''}")
            
            # Verificar si tiene migraciones pendientes
            try:
                count = modelo.objects.count()
                print(f"   📊 Registros: {count}")
            except Exception as e:
                print(f"   ⚠️  Error accediendo a tabla: {e}")
        
        # Verificar específicamente los modelos que necesitamos
        modelos_necesarios = ['Alumno', 'SolicitudRecarga', 'Transaccion']
        print(f"\n🎯 VERIFICACIÓN DE MODELOS NECESARIOS")
        print("=" * 40)
        
        for nombre_modelo in modelos_necesarios:
            try:
                modelo = getattr(models, nombre_modelo)
                print(f"✅ {nombre_modelo}: EXISTE")
                
                # Verificar campos específicos para cada modelo
                if nombre_modelo == 'Alumno':
                    campos_saldo = ['saldo_tarjeta', 'numero_tarjeta', 'limite_consumo']
                    for campo in campos_saldo:
                        if hasattr(modelo, campo):
                            print(f"   ✅ Campo {campo}: OK")
                        else:
                            print(f"   ❌ Campo {campo}: FALTA")
                
                elif nombre_modelo == 'Transaccion':
                    campos_transaccion = ['tipo', 'monto', 'saldo_anterior', 'saldo_posterior']
                    for campo in campos_transaccion:
                        if campo in [f.name for f in modelo._meta.fields]:
                            print(f"   ✅ Campo {campo}: OK")
                        else:
                            print(f"   ❌ Campo {campo}: FALTA")
                
            except AttributeError:
                print(f"❌ {nombre_modelo}: NO EXISTE")
        
        return modelo_classes
        
    except Exception as e:
        print(f"❌ Error verificando modelos: {e}")
        return []

def verificar_importaciones_views():
    """Verificar qué está tratando de importar views.py"""
    print(f"\n🔍 VERIFICANDO IMPORTACIONES EN VIEWS.PY")
    print("=" * 50)
    
    try:
        with open('alumnos/views.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar líneas de importación
        lineas = contenido.split('\n')
        importando = False
        
        for i, linea in enumerate(lineas, 1):
            if 'from .models import' in linea or 'from alumnos.models import' in linea:
                importando = True
                print(f"📋 Línea {i}: {linea.strip()}")
            elif importando and linea.strip().startswith((')', '#', 'from', 'import')):
                if linea.strip().startswith(')'):
                    print(f"📋 Línea {i}: {linea.strip()}")
                    importando = False
                elif not linea.strip().startswith('#'):
                    importando = False
            elif importando:
                print(f"📋 Línea {i}: {linea.strip()}")
        
        # Buscar referencias a TransaccionSaldo
        if 'TransaccionSaldo' in contenido:
            print(f"\n⚠️  ENCONTRADAS REFERENCIAS A 'TransaccionSaldo':")
            for i, linea in enumerate(lineas, 1):
                if 'TransaccionSaldo' in linea:
                    print(f"   Línea {i}: {linea.strip()}")
        else:
            print(f"\n✅ No se encontraron referencias a 'TransaccionSaldo'")
        
    except FileNotFoundError:
        print("❌ No se encontró el archivo views.py")
    except Exception as e:
        print(f"❌ Error leyendo views.py: {e}")

if __name__ == "__main__":
    modelos = verificar_modelos_existentes()
    verificar_importaciones_views()
    
    print(f"\n🚀 SIGUIENTES PASOS RECOMENDADOS:")
    print("=" * 40)
    print("1. Corregir importaciones en views.py")
    print("2. Agregar solo los modelos faltantes")
    print("3. Ejecutar makemigrations")
    print("4. Aplicar migrate")