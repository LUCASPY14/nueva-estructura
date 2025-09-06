from django import forms
from django.forms.models import inlineformset_factory
from .models import Venta, DetalleVenta, Pago

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['alumno', 'condicion']

DetalleFormSet = inlineformset_factory(
    Venta, DetalleVenta,
    fields=['producto', 'cantidad', 'precio_unitario'],
    extra=1,
    can_delete=True,
    widgets={
        'producto': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
        'cantidad': forms.NumberInput(attrs={'class': 'border rounded p-2 w-24'}),
        'precio_unitario': forms.NumberInput(attrs={'class': 'border rounded p-2 w-32'}),
    }
)

PagoFormSet = inlineformset_factory(
    Venta, Pago,
    fields=['metodo', 'monto', 'observacion'],
    extra=1,
    can_delete=True,
    widgets={
        'metodo': forms.Select(attrs={'class': 'border rounded p-2'}),
        'monto': forms.NumberInput(attrs={'class': 'border rounded p-2 w-32'}),
        'observacion': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
    }
)

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['metodo', 'monto', 'observacion']

    def clean_monto(self):
        monto = self.cleaned_data['monto']
        if monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor a cero.")
        return monto
