from django import forms
from django.forms import inlineformset_factory
from .models import Venta, DetalleVenta
from productos.models import Producto
from alumnos.models import Alumno

class VentaForm(forms.ModelForm):
    """Formulario para crear y editar ventas"""
    
    class Meta:
        model = Venta
        fields = [
            'alumno',
            'tipo_pago',
            'descuento',
            'notas',
        ]
        widgets = {
            'alumno': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Seleccionar alumno (opcional)'
            }),
            'tipo_pago': forms.Select(attrs={
                'class': 'form-control'
            }),
            'descuento': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'value': '0.00'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Usar el campo correcto según el modelo Alumno
        self.fields['alumno'].queryset = Alumno.objects.filter(estado='activo')
        self.fields['alumno'].required = False
        self.fields['notas'].required = False
        self.fields['descuento'].required = False

class DetalleVentaForm(forms.ModelForm):
    """Formulario para los detalles de venta"""
    
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-control producto-select'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control cantidad-input',
                'min': '1',
                'value': '1'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(
            activo=True,
            cantidad__gt=0
        )

# Formset para manejar múltiples detalles de venta
DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)

class BuscarProductoForm(forms.Form):
    """Formulario para buscar productos en el punto de venta"""
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar producto por nombre o código...',
            'autocomplete': 'off'
        })
    )

class BuscarAlumnoForm(forms.Form):
    """Formulario para buscar alumnos"""
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar alumno por nombre, apellido o DNI...',
            'autocomplete': 'off'
        })
    )

class FiltroVentasForm(forms.Form):
    """Formulario para filtrar ventas"""
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos')] + Venta.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    tipo_pago = forms.ChoiceField(
        choices=[('', 'Todos')] + Venta.TIPO_PAGO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

class PuntoVentaForm(forms.Form):
    """Formulario simplificado para el punto de venta"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar el queryset en __init__ para evitar problemas de importación
        self.fields['alumno'].queryset = Alumno.objects.filter(estado='activo')
    
    alumno = forms.ModelChoiceField(
        queryset=Alumno.objects.none(),  # Se establece en __init__
        required=False,
        empty_label="Cliente general",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    tipo_pago = forms.ChoiceField(
        choices=Venta.TIPO_PAGO_CHOICES,
        initial='efectivo',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    descuento = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0,
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        })
    )
