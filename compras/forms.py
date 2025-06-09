# compras/forms.py
from django import forms
from django.forms.models import inlineformset_factory
from .models import Compra, DetalleCompra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor', 'fecha']
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
            'fecha': forms.DateTimeInput(
                attrs={'class': 'border rounded p-2 w-full', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es creación (sin instancia), la fecha por defecto ya viene en now.
        # Ajustamos el formato para el widget datetime-local:
        self.fields['fecha'].input_formats = ['%Y-%m-%dT%H:%M']

# Formset para los detalles de la compra:
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
