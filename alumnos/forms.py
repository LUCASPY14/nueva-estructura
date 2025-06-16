from django import forms
from .models import Alumno, Padre, Restriccion
from decimal import Decimal

class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre', 'numero_tarjeta', 'grado', 'nivel', 'limite_consumo', 'padre']

class PadreForm(forms.ModelForm):
    class Meta:
        model = Padre
        fields = [
            'nombre', 'apellido', 'razon_social', 'ruc',
            'email', 'telefono', 'direccion', 'barrio', 'ciudad'
        ]

class CargarSaldoForm(forms.Form):
    alumno = forms.ModelChoiceField(
        queryset=Alumno.objects.none(),
        label="Alumno",
        widget=forms.Select(attrs={'class': 'border rounded p-2 w-full'})
    )
    monto = forms.DecimalField(
        min_value=Decimal('0.01'),
        decimal_places=2,
        max_digits=12,
        label="Monto a cargar (Gs.)",
        widget=forms.NumberInput(attrs={'class': 'border rounded p-2 w-full'})
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
