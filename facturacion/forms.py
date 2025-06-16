from django import forms
from .models import Factura
from ventas.models import Venta

class FacturaForm(forms.ModelForm):
    venta = forms.ModelChoiceField(
        queryset=Venta.objects.filter(factura__isnull=True),
        label="Venta"
    )
    class Meta:
        model = Factura
        fields = ['venta', 'numero', 'fecha_emision', 'ruc', 'razon_social', 'direccion', 'total']
        widgets = {
            'numero': forms.TextInput(attrs={'class':'border rounded p-2 w-full'}),
            'fecha_emision': forms.DateTimeInput(attrs={'class':'border rounded p-2 w-full', 'type': 'datetime-local'}),
            'ruc': forms.TextInput(attrs={'class':'border rounded p-2 w-full'}),
            'razon_social': forms.TextInput(attrs={'class':'border rounded p-2 w-full'}),
            'direccion': forms.TextInput(attrs={'class':'border rounded p-2 w-full'}),
            'total': forms.NumberInput(attrs={'class':'border rounded p-2 w-full'}),
        }
