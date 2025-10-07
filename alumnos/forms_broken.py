from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import (
    Alumno, Padre, SolicitudRecarga, Transaccion,
    Curso, 
)
from usuarios.models import UsuarioLG
from decimal import Decimal

class AlumnoForm(forms.ModelForm):
    """
    Formulario para crear y editar alumnos.
    """
    class Meta:
        model = Alumno
        fields = [
            'nombre', 'apellido', 'fecha_nacimiento', 'sexo',
            'curso', 'numero_matricula', 'telefono', 'email', 
            'direccion', 'numero_tarjeta', 'limite_consumo', 
            'estado', 'notas'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese el apellido'
            }),
            'numero_matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 2024-001'
            }),
            'numero_tarjeta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de tarjeta'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(021) 123-456'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'alumno@email.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales'
            }),
            'limite_consumo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0 = sin límite',
                'min': '0',
                'step': '1000'
            })
        }

    def clean_numero_matricula(self):
        numero = self.cleaned_data['numero_matricula']
        # Verificar formato básico
        if len(numero) < 4:
            raise ValidationError('El número de matrícula debe tener al menos 4 caracteres')
        return numero.upper()

    def clean_numero_tarjeta(self):
        numero_tarjeta = self.cleaned_data.get('numero_tarjeta')
        if numero_tarjeta:
            # Verificar que no esté en uso por otro alumno
            if self.instance.pk:
                if Alumno.objects.exclude(pk=self.instance.pk).filter(numero_tarjeta=numero_tarjeta).exists():
                    raise ValidationError('Este número de tarjeta ya está en uso')
            else:
                if Alumno.objects.filter(numero_tarjeta=numero_tarjeta).exists():
                    raise ValidationError('Este número de tarjeta ya está en uso')
        return numero_tarjeta

class PadreForm(forms.ModelForm):
    """
    Formulario para registrar padres.
    """
    class Meta:
        model = Padre
        fields = ['nombre', 'apellido', 'telefono', 'email', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(021) 123-456'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'padre@email.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }

# NUEVOS FORMULARIOS PARA EL SISTEMA DE CARGA DE SALDO

class SolicitudRecargaForm(forms.ModelForm):
    """
    Formulario para que padres soliciten recargas de saldo.
    """
    class Meta:
        model = SolicitudRecarga
        fields = [
            'alumno', 'monto_solicitado', 'metodo_pago', 
            'referencia_pago', 'comprobante_pago'
        ]
        widgets = {
            'alumno': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'monto_solicitado': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1000',
                'step': '1000',
                'placeholder': 'Ingrese el monto en guaraníes',
                'required': True
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'referencia_pago': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de comprobante/referencia'
            }),
            'comprobante_pago': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png,.pdf',
                'required': True
            })
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si es un padre, solo mostrar sus hijos
        if user and user.is_padre():
            # Obtener alumnos relacionados con este padre
            padres = Padre.objects.filter(
                email=user.email  # Asumiendo que el email coincide
            )
            if padres.exists():
                alumnos_ids = []
                for padre in padres:
                    alumnos_ids.extend(padre.alumnos.values_list('id', flat=True))
                
                self.fields['alumno'].queryset = Alumno.objects.filter(
                    id__in=alumnos_ids,
                    estado='activo'
                )
            else:
                # Si no hay padre asociado, no mostrar alumnos
                self.fields['alumno'].queryset = Alumno.objects.none()
        
        # Personalizar etiquetas
        self.fields['alumno'].label = 'Seleccione el alumno'
        self.fields['monto_solicitado'].label = 'Monto a recargar (Gs.)'
        self.fields['metodo_pago'].label = 'Método de pago'
        self.fields['referencia_pago'].label = 'Referencia del pago'
        self.fields['comprobante_pago'].label = 'Comprobante de pago'
        
        # Ayuda contextual
        self.fields['comprobante_pago'].help_text = (
            "Suba una imagen clara del comprobante de pago. "
            "Formatos aceptados: JPG, PNG, PDF (máx. 5MB)"
        )

    def clean_monto_solicitado(self):
        monto = self.cleaned_data['monto_solicitado']
        
        # Validar monto mínimo
        if monto < 1000:
            raise ValidationError('El monto mínimo de recarga es 1.000 Gs.')
        
        # Validar monto máximo (opcional)
        if monto > 1000000:
            raise ValidationError('El monto máximo de recarga es 1.000.000 Gs.')
        
        return monto

    def clean_comprobante(self):
        comprobante = self.cleaned_data.get('comprobante_pago')
        
        if comprobante:
            # Validar tamaño (5MB máximo)
            if comprobante.size > 5 * 1024 * 1024:
                raise ValidationError('El archivo no puede ser mayor a 5MB.')
            
            # Validar tipo de archivo
            allowed_types = [
                'image/jpeg', 'image/jpg', 'image/png', 
                'application/pdf'
            ]
            if comprobante.content_type not in allowed_types:
                raise ValidationError(
                    'Tipo de archivo no válido. '
                    'Use JPG, PNG o PDF únicamente.'
                )
        
        return comprobante

class ProcesarSolicitudForm(forms.ModelForm):
    """
    Formulario para que administradores procesen solicitudes de recarga.
    """
    class Meta:
        model = SolicitudRecarga
        fields = [
            'estado', 'monto_aprobado', 'observaciones_procesamiento'
        ]
        widgets = {
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'monto_aprobado': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1000',
                'placeholder': 'Monto a aprobar (puede ser diferente al solicitado)'
            }),
            'observaciones_procesamiento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observaciones sobre la aprobación/rechazo'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Solo mostrar estados relevantes para procesamiento
        self.fields['estado'].choices = [
            ('aprobada', 'Aprobar'),
            ('rechazada', 'Rechazar'),
        ]
        
        self.fields['monto_aprobado'].required = False
        self.fields['observaciones_procesamiento'].required = True

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        monto_aprobado = cleaned_data.get('monto_aprobado')
        
        if estado == 'aprobada':
            if not monto_aprobado or monto_aprobado <= 0:
                raise ValidationError({
                    'monto_aprobado': 'Debe especificar un monto válido para aprobar la solicitud.'
                })
        
        return cleaned_data

class TransaccionForm(forms.ModelForm):
    """
    Formulario para crear transacciones manuales de saldo.
    """
    class Meta:
        model = Transaccion
        fields = [
            'alumno', 'tipo', 'monto', 'descripcion'
        ]
        widgets = {
            'alumno': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1000',
                'placeholder': 'Monto (positivo para crédito, negativo para débito)'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la transacción'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Solo permitir ciertos tipos de transacción manual
        self.fields['tipo'].choices = [
            ('ajuste_positivo', 'Ajuste Positivo'),
            ('ajuste_negativo', 'Ajuste Negativo'),
            ('devolucion', 'Devolución'),
        ]
        
        self.fields['alumno'].queryset = Alumno.objects.filter(estado='activo')

class BusquedaAlumnoForm(forms.Form):
    """
    Formulario para buscar alumnos.
    """
    busqueda = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, apellido, número de matrícula o tarjeta...',
            'autocomplete': 'off'
        })
    )
    
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        required=False,
        empty_label='Todos los cursos',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + list(Alumno.ESTADO_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ConsultaSaldoForm(forms.Form):
    """
    Formulario para consultar saldo por número de tarjeta.
    """
    numero_tarjeta = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el número de tarjeta',
            'autocomplete': 'off'
        }),
        label='Número de Tarjeta'
    )

    def clean_numero_tarjeta(self):
        numero = self.cleaned_data['numero_tarjeta']
        
        try:
            alumno = Alumno.objects.get(
                numero_tarjeta=numero,
                estado='activo'
            )
        except Alumno.DoesNotExist:
            raise ValidationError(
                'No se encontró un alumno activo con este número de tarjeta.'
            )
        
        return numero

# Mantener compatibilidad con el archivo views.py existente
class CargaSaldoForm(forms.Form):
    monto = forms.DecimalField(
        max_digits=10,
        decimal_places=0,
        min_value=100,
        max_value=500000,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500',
            'placeholder': 'Ej: 10000',
            'id': 'id_monto',
            'step': '100',
            'min': '100',
            'max': '500000'
        }),
        label='Monto a Cargar ($)',
        help_text='Monto entre $100 y $500.000'
    )
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto:
            if monto < 100:
                raise forms.ValidationError("El monto mínimo es $100")
            if monto > 500000:
                raise forms.ValidationError("El monto máximo es $500.000")
        return monto

class': 'form-control'})
    )
    monto = forms.DecimalField(
        max_digits=10,
        decimal_places=0,
        min_value=100,
        max_value=500000,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500',
            'placeholder': 'Ej: 10000',
            'id': 'id_monto',
            'step': '100',
            'min': '100',
            'max': '500000'
        }),
        label='Monto a Cargar ($)',
        help_text='Monto entre $100 y $500.000'
    )
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto:
            if monto < 100:
                raise forms.ValidationError("El monto mínimo es $100")
            if monto > 500000:
                raise forms.ValidationError("El monto máximo es $500.000")
            if monto % 100 != 0:
                raise forms.ValidationError("El monto debe ser múltiplo de $100")
        return monto
