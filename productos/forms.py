# productos/forms.py
from django import forms
from .models import Producto, Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'border rounded p-2 w-full',
                'placeholder': 'Nombre del proveedor'
            }),
            'contacto': forms.TextInput(attrs={
                'class': 'border rounded p-2 w-full',
                'placeholder': 'Teléfono o email (opcional)'
            }),
        }

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
            'proveedor'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'border rounded p-2 w-full',
                'placeholder': 'Código del producto (p.ej. ABC123)'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'border rounded p-2 w-full',
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'border rounded p-2 w-full',
                'rows': 3,
                'placeholder': 'Descripción breve (opcional)'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'border rounded p-2 w-32',
                'placeholder': 'Unidades'
            }),
            'precio_costo': forms.NumberInput(attrs={
                'class': 'border rounded p-2 w-32',
                'placeholder': 'Costo Gs.'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'border rounded p-2 w-32',
                'placeholder': 'Venta Gs.'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'border rounded p-2 w-full',
                'placeholder': 'Categoría (p.ej. Bebidas)'
            }),
            'proveedor': forms.Select(attrs={
                'class': 'border rounded p-2 w-full'
            }),
        }
