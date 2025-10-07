from .models import Venta, DetalleVenta, PagoVenta, Caja, TurnoCajero, MetodoPago
from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from decimal import Decimal

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'descuento', 'observaciones']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario', 'descuento_item']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descuento_item': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class PagoVentaForm(forms.ModelForm):
    class Meta:
        model = PagoVenta
        fields = ['metodo_pago', 'metodo', 'monto', 'referencia', 'observacion']
        widgets = {
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'metodo': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'observacion': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TurnoCajeroForm(forms.ModelForm):
    class Meta:
        model = TurnoCajero
        fields = ['caja', 'monto_inicial', 'observaciones_apertura']
        widgets = {
            'caja': forms.Select(attrs={'class': 'form-control'}),
            'monto_inicial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observaciones_apertura': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Formsets
DetalleFormSet = inlineformset_factory(
    Venta, 
    DetalleVenta, 
    form=DetalleVentaForm,
    extra=1, 
    can_delete=True
)

PagoFormSet = inlineformset_factory(
    Venta, 
    PagoVenta, 
    form=PagoVentaForm,
    extra=1, 
    can_delete=True
)
