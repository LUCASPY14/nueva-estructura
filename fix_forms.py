"""
Corrector para forms.py
"""

def fix_forms():
    """Corregir importaciones en forms.py"""
    print("🔧 Corrigiendo forms.py...")
    
    try:
        # Leer archivo actual
        with open('alumnos/forms.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Hacer backup
        with open('alumnos/forms.py.backup', 'w', encoding='utf-8') as f:
            f.write(contenido)
        print("   📋 Backup creado: forms.py.backup")
        
        # Realizar reemplazos
        reemplazos = [
            ('TransaccionSaldo', 'Transaccion'),
            ('from .models import (\n    Alumno,\n    SolicitudRecarga,\n    TransaccionSaldo,', 
             'from .models import (\n    Alumno,\n    SolicitudRecarga,\n    Transaccion,'),
        ]
        
        contenido_corregido = contenido
        cambios_realizados = 0
        
        for buscar, reemplazar in reemplazos:
            if buscar in contenido_corregido:
                contenido_corregido = contenido_corregido.replace(buscar, reemplazar)
                cambios_realizados += 1
                print(f"   ✅ Reemplazado: {buscar[:50]}...")
        
        # Si no hay cambios específicos, hacer reemplazo general
        if cambios_realizados == 0 and 'TransaccionSaldo' in contenido:
            contenido_corregido = contenido_corregido.replace('TransaccionSaldo', 'Transaccion')
            print("   ✅ Reemplazo general de TransaccionSaldo por Transaccion")
        
        # Escribir archivo corregido
        with open('alumnos/forms.py', 'w', encoding='utf-8') as f:
            f.write(contenido_corregido)
        
        print("   ✅ forms.py corregido")
        return True
        
    except FileNotFoundError:
        print("   ℹ️  forms.py no encontrado - creando archivo básico")
        return crear_forms_basico()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def crear_forms_basico():
    """Crear un forms.py básico si no existe o tiene problemas"""
    forms_content = '''from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Alumno,
    SolicitudRecarga,
    Transaccion,
)

class SolicitudRecargaForm(forms.ModelForm):
    """Formulario para solicitar recarga de saldo"""
    
    class Meta:
        model = SolicitudRecarga
        fields = [
            'alumno', 'monto_solicitado', 'metodo_pago', 
            'comprobante_pago', 'numero_comprobante'
        ]
        widgets = {
            'monto_solicitado': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el monto en guaraníes',
                'min': '1000',
                'step': '1000'
            }),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'comprobante_pago': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf'
            }),
            'numero_comprobante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de comprobante (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar solo los alumnos relacionados con este usuario
            self.fields['alumno'].queryset = Alumno.objects.filter(
                padres=user, 
                estado='activo'
            )
            self.fields['alumno'].widget.attrs.update({'class': 'form-control'})

class ConsultaSaldoForm(forms.Form):
    """Formulario para consultar saldo por número de tarjeta"""
    
    numero_tarjeta = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el número de tarjeta',
            'autocomplete': 'off'
        }),
        label="Número de Tarjeta"
    )
    
    def clean_numero_tarjeta(self):
        numero = self.cleaned_data['numero_tarjeta'].strip()
        
        if not numero:
            raise forms.ValidationError("El número de tarjeta es requerido")
        
        try:
            alumno = Alumno.objects.get(numero_tarjeta=numero, estado='activo')
            return numero
        except Alumno.DoesNotExist:
            raise forms.ValidationError("Número de tarjeta no encontrado o inactivo")

class TransaccionForm(forms.ModelForm):
    """Formulario para registrar transacciones"""
    
    class Meta:
        model = Transaccion
        fields = [
            'alumno', 'tipo', 'monto', 'descripcion', 'observaciones'
        ]
        widgets = {
            'alumno': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '1000'
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la transacción'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones (opcional)'
            }),
        }
'''
    
    try:
        with open('alumnos/forms.py', 'w', encoding='utf-8') as f:
            f.write(forms_content)
        print("   ✅ forms.py básico creado")
        return True
    except Exception as e:
        print(f"   ❌ Error creando forms.py: {e}")
        return False

def verificar_otros_archivos():
    """Verificar otros archivos que puedan tener referencias incorrectas"""
    print("\n🔍 Verificando otros archivos...")
    
    archivos_a_verificar = [
        'alumnos/admin.py',
        'alumnos/urls.py',
        'alumnos/views.py'
    ]
    
    for archivo in archivos_a_verificar:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            if 'TransaccionSaldo' in contenido:
                print(f"   ⚠️  {archivo} contiene 'TransaccionSaldo'")
                
                # Hacer backup y corregir
                with open(f"{archivo}.backup", 'w', encoding='utf-8') as f:
                    f.write(contenido)
                
                contenido_corregido = contenido.replace('TransaccionSaldo', 'Transaccion')
                
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido_corregido)
                
                print(f"   ✅ {archivo} corregido")
            else:
                print(f"   ✅ {archivo} está limpio")
                
        except FileNotFoundError:
            print(f"   ℹ️  {archivo} no encontrado")
        except Exception as e:
            print(f"   ❌ Error en {archivo}: {e}")

if __name__ == "__main__":
    print("🚀 CORRECTOR DE FORMS.PY Y OTROS ARCHIVOS")
    print("=" * 50)
    
    # 1. Corregir forms.py
    success = fix_forms()
    
    # 2. Verificar otros archivos
    verificar_otros_archivos()
    
    if success:
        print(f"\n✅ CORRECCIÓN COMPLETADA")
        print("Próximo paso: python manage.py makemigrations alumnos")
    else:
        print(f"\n❌ HUBO ERRORES")
        print("Revisa los archivos manualmente")