from django import forms
from .models import Factura
from ventas.models import Venta

BASE_INPUT_CLASSES = 'border border-gray-300 rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-green-500'

class FacturaForm(forms.ModelForm):
    venta = forms.ModelChoiceField(
        queryset=Venta.objects.filter(factura__isnull=True),
        label="Venta",
        widget=forms.Select(attrs={'class': BASE_INPUT_CLASSES})
    )

    class Meta:
        model = Factura
        fields = ['venta', 'numero', 'fecha_emision', 'ruc', 'razon_social', 'direccion', 'total']
        widgets = {
            'numero': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'fecha_emision': forms.DateTimeInput(attrs={'class': BASE_INPUT_CLASSES, 'type': 'datetime-local'}),
            'ruc': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'razon_social': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'direccion': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'total': forms.NumberInput(attrs={'class': BASE_INPUT_CLASSES}),
        }
