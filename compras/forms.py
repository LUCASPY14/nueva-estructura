from django import forms
from django.forms.models import inlineformset_factory
from .models import Compra, DetalleCompra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor']
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
        }

# Formset para los detalles de la compra
DetalleCompraFormSet = inlineformset_factory(
    Compra,
    DetalleCompra,
    fields=['producto', 'cantidad', 'precio_unitario'],
    extra=1,
    can_delete=True,
    widgets={
        'producto': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
        'cantidad': forms.NumberInput(attrs={'class': 'border rounded p-2 w-24'}),
        'precio_unitario': forms.NumberInput(attrs={'class': 'border rounded p-2 w-32'}),
    }
)
