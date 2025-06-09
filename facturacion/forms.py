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
        fields = ['venta', 'numero', 'formato']
        widgets = {
            'numero': forms.TextInput(attrs={'class':'border rounded p-2 w-full'}),
            'formato': forms.Select(attrs={'class':'border rounded p-2'}),
        }