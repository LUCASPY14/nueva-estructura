from django import forms
from compras.models import Proveedor
from .models import Producto

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto']  # Solo si 'contacto' existe en tu modelo
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'border rounded p-2 w-full',
                'placeholder': 'Nombre del proveedor'
            }),
            # Solo si tu modelo tiene el campo contacto
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
            'cantidad',         # Cambia a 'stock' si tu modelo lo usa así
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
             # AQUI la corrección: Select para FK
            'categoria': forms.Select(attrs={
                'class': 'border rounded p-2 w-full'
            }),
            'proveedor': forms.Select(attrs={
                'class': 'border rounded p-2 w-full'
            }),
        }
