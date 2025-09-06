from django import forms
from django.forms.models import inlineformset_factory
from .models import Compra, DetalleCompra

# Clase base de estilos
BASE_INPUT_CLASSES = 'border border-gray-300 rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-green-500'

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor']
        widgets = {
            'proveedor': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
        }

# Formset para los detalles de la compra
DetalleCompraFormSet = inlineformset_factory(
    Compra,
    DetalleCompra,
    fields=['producto', 'cantidad', 'precio_unitario'],
    extra=1,
    can_delete=True,
    widgets={
        'producto': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
        'cantidad': forms.NumberInput(attrs={'class': 'border border-gray-300 rounded-lg px-3 py-2 w-24 focus:outline-none focus:ring-2 focus:ring-green-500'}),
        'precio_unitario': forms.NumberInput(attrs={'class': 'border border-gray-300 rounded-lg px-3 py-2 w-32 focus:outline-none focus:ring-2 focus:ring-green-500'}),
    }
)
