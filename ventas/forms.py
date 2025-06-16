from django import forms
from django.forms.models import inlineformset_factory
from .models import Venta, DetalleVenta, Pago, AuthorizationCode
from alumnos.models import Alumno

class VentaForm(forms.ModelForm):
    codigo_autorizacion = forms.CharField(
        max_length=32, required=False,
        help_text="Si falta saldo, ingresa código de autorización de Admin"
    )

    class Meta:
        model = Venta
        fields = ['alumno', 'condicion', 'codigo_autorizacion']
        widgets = {
            'alumno': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
            'condicion': forms.Select(attrs={'class': 'border rounded p-2'}),
        }

    def clean_codigo_autorizacion(self):
        code = self.cleaned_data['codigo_autorizacion']
        if code:
            try:
                auth = AuthorizationCode.objects.get(codigo=code)
                return auth
            except AuthorizationCode.DoesNotExist:
                raise forms.ValidationError("Código inválido o inactivo")
        return None

# Formset para detalles de la venta (productos vendidos)
DetalleFormSet = inlineformset_factory(
    Venta, DetalleVenta,
    fields=['producto', 'cantidad', 'precio_unitario'],
    extra=1, can_delete=True,
    widgets={
        'producto': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
        'cantidad': forms.NumberInput(attrs={'class': 'border rounded p-2 w-24'}),
        'precio_unitario': forms.NumberInput(attrs={'class': 'border rounded p-2 w-32'}),
    }
)

# Formset para pagos (ajustado: SOLO los campos que existen en tu modelo Pago)
PagoFormSet = inlineformset_factory(
    Venta, Pago,
    fields=['metodo', 'monto', 'observacion'],
    extra=1, can_delete=True,
    widgets={
        'metodo': forms.Select(attrs={'class': 'border rounded p-2'}),
        'monto': forms.NumberInput(attrs={'class': 'border rounded p-2 w-32'}),
        'observacion': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
    }
)
