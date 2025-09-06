from django import forms
from .models import Alumno, Padre, Restriccion
from decimal import Decimal

BASE_INPUT_CLASSES = 'border border-gray-300 rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-green-500'

class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre', 'numero_tarjeta', 'grado', 'nivel', 'limite_consumo', 'padre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'numero_tarjeta': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'grado': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'nivel': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
            'limite_consumo': forms.NumberInput(attrs={'class': BASE_INPUT_CLASSES}),
            'padre': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
        }

class PadreForm(forms.ModelForm):
    class Meta:
        model = Padre
        fields = [
            'nombre', 'apellido', 'razon_social', 'ruc',
            'email', 'telefono', 'direccion', 'barrio', 'ciudad'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'apellido': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'razon_social': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'ruc': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'email': forms.EmailInput(attrs={'class': BASE_INPUT_CLASSES}),
            'telefono': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'direccion': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'barrio': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'ciudad': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
        }

class CargarSaldoForm(forms.Form):
    alumno = forms.ModelChoiceField(
        queryset=Alumno.objects.none(),
        label="Alumno",
        widget=forms.Select(attrs={'class': BASE_INPUT_CLASSES})
    )
    monto = forms.DecimalField(
        min_value=Decimal('0.01'),
        decimal_places=2,
        max_digits=12,
        label="Monto a cargar (Gs.)",
        widget=forms.NumberInput(attrs={'class': BASE_INPUT_CLASSES})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'padre_profile'):
            self.fields['alumno'].queryset = user.padre_profile.alumnos.all()
        else:
            self.fields['alumno'].queryset = Alumno.objects.all()

class RestriccionForm(forms.ModelForm):
    class Meta:
        model = Restriccion
        fields = ['alumno', 'producto', 'permitido']
        widgets = {
            'alumno': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
            'producto': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
            'permitido': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-green-600 focus:ring-green-500'
            }),
        }
