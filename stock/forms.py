from django import forms
from .models import MovimientoStock

BASE_INPUT_CLASSES = 'border border-gray-300 rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-green-500'

class MovimientoStockForm(forms.ModelForm):
    class Meta:
        model = MovimientoStock
        fields = ['producto', 'cantidad', 'tipo', 'referencia']
        widgets = {
            'producto': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
            'cantidad': forms.NumberInput(attrs={'class': BASE_INPUT_CLASSES}),
            'tipo': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
            'referencia': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
        }
