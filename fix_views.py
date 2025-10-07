"""
Corrector para views.py
"""

def fix_views():
    try:
        with open('alumnos/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup
        with open('alumnos/views.py.backup', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Reemplazos necesarios
        replacements = [
            ('TransaccionSaldo', 'Transaccion'),
            ('from .models import (\n    Alumno,', 'from .models import (\n    Alumno, SolicitudRecarga, Transaccion,'),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Escribir archivo corregido
        with open('alumnos/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ views.py corregido")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_views()