from django import forms
from .models import MovimientoStock

class MovimientoStockForm(forms.ModelForm):
    class Meta:
        model = MovimientoStock
        fields = ['producto', 'tipo', 'cantidad', 'motivo', 'referencia']
        widgets = {
            'producto': forms.Select(attrs={'class':'border rounded p-2 w-full'}),
            'tipo': forms.Select(attrs={'class':'border rounded p-2'}),
            'cantidad': forms.NumberInput(attrs={'class':'border rounded p-2 w-24'}),
            'motivo': forms.TextInput(attrs={'class':'border rounded p-2 w-full', 'placeholder':'Ej. Ajuste físico'}),
            'referencia': forms.TextInput(attrs={'class':'border rounded p-2 w-full', 'placeholder':'ID Compra/Venta'}),
        }