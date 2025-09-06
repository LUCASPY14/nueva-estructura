from django import forms
from .models import Producto, Categoria
from proveedores.models import Proveedor

BASE_INPUT_CLASSES = 'border border-gray-300 rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-green-500'

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'codigo',
            'nombre',
            'descripcion',
            'cantidad',
            'precio_costo',
            'precio_venta',
            'categoria',
            'proveedor',
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': BASE_INPUT_CLASSES,
                'placeholder': 'Código del producto (p.ej. ABC123)'
            }),
            'nombre': forms.TextInput(attrs={
                'class': BASE_INPUT_CLASSES,
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': BASE_INPUT_CLASSES,
                'rows': 3,
                'placeholder': 'Descripción breve (opcional)'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': BASE_INPUT_CLASSES,
                'placeholder': 'Unidades'
            }),
            'precio_costo': forms.NumberInput(attrs={
                'class': BASE_INPUT_CLASSES,
                'placeholder': 'Costo Gs.'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': BASE_INPUT_CLASSES,
                'placeholder': 'Venta Gs.'
            }),
            'categoria': forms.Select(attrs={
                'class': BASE_INPUT_CLASSES
            }),
            'proveedor': forms.Select(attrs={
                'class': BASE_INPUT_CLASSES
            }),
        }
