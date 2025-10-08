from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import (
    Alumno, Padre, SolicitudRecarga, Transaccion,
    Curso, 
)
from usuarios.models import CustomUser
from decimal import Decimal

class AlumnoForm(forms.ModelForm):
    """
    Formulario para crear y editar alumnos.
    """
    class Meta:
        model = Alumno
        fields = [
            'nombre', 'apellido', 'fecha_nacimiento', 'sexo',
            'curso', 'telefono', 'email', 'direccion', 
            'numero_tarjeta', 'limite_consumo', 'estado', 'notas'
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
        if len(numero) < 4:
            raise ValidationError('El número de matrícula debe tener al menos 4 caracteres')
        return numero.upper()

    def clean_numero_tarjeta(self):
        numero_tarjeta = self.cleaned_data.get('numero_tarjeta')
        if numero_tarjeta:
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

class CargaSaldoForm(forms.Form):
    """
    Formulario para cargar saldo a un alumno.
    """
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
                'placeholder': 'Monto a aprobar'
            }),
            'observaciones_procesamiento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observaciones sobre la aprobación/rechazo'
            })
        }

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
                'placeholder': 'Monto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la transacción'
            })
        }

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

class MisTransaccionesFilterForm(forms.Form):
    """
    Formulario para filtrar transacciones por alumno en la vista de padres
    """
    alumno = forms.ModelChoiceField(
        queryset=None,  # Se configurará dinámicamente en la vista
        required=False,
        empty_label="Todos los alumnos",
        widget=forms.Select(attrs={
            'class': 'border rounded px-3 py-2',
            'id': 'alumno'
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'padre_profile'):
            # Filtrar solo alumnos del padre logueado
            self.fields['alumno'].queryset = user.padre_profile.alumnos.filter(estado='activo')
        else:
            self.fields['alumno'].queryset = Alumno.objects.filter(estado='activo')

class SolicitudCargaSaldoForm(forms.ModelForm):
    """
    Formulario para que padres soliciten carga de saldo
    """
    class Meta:
        model = SolicitudRecarga
        fields = ['alumno', 'monto_solicitado', 'metodo_pago', 'referencia_pago', 'comprobante_pago']
        widgets = {
            'alumno': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'required': True
            }),
            'monto_solicitado': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '1000',
                'step': '1000',
                'placeholder': 'Monto en guaraníes (mín. 1.000)',
                'required': True
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'required': True
            }),
            'referencia_pago': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Número de comprobante, referencia, etc.',
                'maxlength': 100
            }),
            'comprobante_pago': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'accept': '.jpg,.jpeg,.png,.pdf',
                'required': True
            })
        }
        labels = {
            'alumno': 'Alumno',
            'monto_solicitado': 'Monto a solicitar (Gs.)',
            'metodo_pago': 'Método de pago',
            'referencia_pago': 'Referencia de pago',
            'comprobante_pago': 'Comprobante de pago'
        }
        help_texts = {
            'monto_solicitado': 'Monto mínimo: 1.000 Gs.',
            'comprobante_pago': 'Formatos permitidos: JPG, PNG, PDF (máx. 5MB)',
            'referencia_pago': 'Número de transacción, comprobante o referencia del pago'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'padre_profile'):
            # Filtrar solo alumnos del padre logueado
            self.fields['alumno'].queryset = user.padre_profile.alumnos.filter(estado='activo')
        else:
            self.fields['alumno'].queryset = Alumno.objects.filter(estado='activo')

    def clean_monto_solicitado(self):
        monto = self.cleaned_data.get('monto_solicitado')
        if monto and monto < 1000:
            raise ValidationError('El monto mínimo es de 1.000 Gs.')
        if monto and monto > 1000000:
            raise ValidationError('El monto máximo es de 1.000.000 Gs.')
        return monto

    def clean_comprobante_pago(self):
        archivo = self.cleaned_data.get('comprobante_pago')
        if archivo:
            # Validar tamaño (máx 5MB)
            if archivo.size > 5 * 1024 * 1024:
                raise ValidationError('El archivo no puede superar los 5MB.')
            
            # Validar tipo de archivo
            tipos_permitidos = ['image/jpeg', 'image/png', 'application/pdf']
            if archivo.content_type not in tipos_permitidos:
                raise ValidationError('Solo se permiten archivos JPG, PNG o PDF.')
        
        return archivo

class HistorialTransaccionesFilterForm(forms.Form):
    """
    Formulario para filtrar historial de transacciones
    """
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'border rounded px-3 py-2'
        }),
        label='Desde'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'border rounded px-3 py-2'
        }),
        label='Hasta'
    )
    
    tipo_transaccion = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + [
            ('recarga', 'Recargas'),
            ('consumo', 'Consumos'),
            ('ajuste', 'Ajustes'),
            ('devolucion', 'Devoluciones')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'border rounded px-3 py-2'
        }),
        label='Tipo'
    )

class DashboardPadreFilterForm(forms.Form):
    """
    Formulario para filtros en dashboard de padres
    """
    mes = forms.ChoiceField(
        choices=[('', 'Todos los meses')] + [
            (str(i), f'{i:02d}') for i in range(1, 13)
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'border rounded px-2 py-1'}),
        label='Mes'
    )
    
    año = forms.ChoiceField(
        choices=[('', 'Todos los años')] + [
            (str(year), str(year)) for year in range(2020, 2030)
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'border rounded px-2 py-1'}),
        label='Año'
    )

class DashboardAdminFilterForm(forms.Form):
    """
    Formulario para filtros en dashboard administrativo
    """
    periodo = forms.ChoiceField(
        choices=[
            ('hoy', 'Hoy'),
            ('semana', 'Esta semana'),
            ('mes', 'Este mes'),
            ('trimestre', 'Este trimestre'),
            ('año', 'Este año'),
            ('personalizado', 'Período personalizado')
        ],
        initial='mes',
        widget=forms.Select(attrs={'class': 'border rounded px-3 py-2'}),
        label='Período'
    )
    
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        required=False,
        empty_label="Todos los cursos",
        widget=forms.Select(attrs={'class': 'border rounded px-3 py-2'}),
        label='Curso'
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'border rounded px-3 py-2'
        }),
        label='Desde'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'border rounded px-3 py-2'
        }),
        label='Hasta'
    )

class EliminarAlumnoForm(forms.Form):
    """
    Formulario de confirmación para eliminar alumno
    """
    confirmar = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'mr-2'
        }),
        label='Confirmo que deseo eliminar este alumno y todas sus transacciones asociadas'
    )
    
    motivo = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md',
            'rows': 3,
            'placeholder': 'Motivo de la eliminación (opcional)'
        }),
        label='Motivo'
    )

# ==========================================
# FORMULARIOS ADICIONALES PARA EL SISTEMA