from django import forms
from .models import Proveedor
from productos.models import ProductoProveedor  # Importación correcta

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'nombre', 'nombre_comercial', 'tipo_documento', 'numero_documento',
            'direccion', 'telefono', 'telefono_alternativo', 'email', 'sitio_web',
            'contacto_nombre', 'contacto_telefono', 'contacto_email',
            'rubro', 'condiciones_pago', 'tiempo_entrega_promedio',
            'notas', 'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_comercial': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_alternativo': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control'}),
            'contacto_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rubro': forms.TextInput(attrs={'class': 'form-control'}),
            'condiciones_pago': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tiempo_entrega_promedio': forms.NumberInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class ProductoProveedorForm(forms.ModelForm):
    class Meta:
        model = ProductoProveedor  # Ahora usa el modelo real
        fields = [
            'producto', 'proveedor', 'codigo_producto_proveedor', 'precio',
            'tiempo_entrega', 'cantidad_minima_pedido', 'notas', 'activo'
        ]
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'codigo_producto_proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tiempo_entrega': forms.NumberInput(attrs={'class': 'form-control'}),
            'cantidad_minima_pedido': forms.NumberInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }