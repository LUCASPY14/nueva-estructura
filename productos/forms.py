from django import forms
from .models import Producto, Categoria, MovimientoStock

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'codigo', 'codigo_barras', 'nombre', 'descripcion', 
            'cantidad', 'cantidad_minima', 'precio_costo', 'precio_venta', 
            'imagen', 'categoria', 'proveedor', 'estado', 'destacado'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'nombre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'rows': 3}),
            'cantidad': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'cantidad_minima': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'precio_costo': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'step': '0.01'}),
            'categoria': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'proveedor': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'estado': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'destacado': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-purple-600 focus:ring-purple-500'}),
        }
        labels = {
            'codigo': 'Código',
            'codigo_barras': 'Código de barras',
            'cantidad_minima': 'Cantidad mínima',
            'precio_costo': 'Precio de costo',
            'precio_venta': 'Precio de venta',
        }
        help_texts = {
            'codigo_barras': 'Código de barras para escanear el producto',
            'cantidad_minima': 'Alerta cuando el stock llegue a este nivel',
            'destacado': 'Marcar como producto destacado',
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'rows': 3}),
            'activa': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-purple-600 focus:ring-purple-500'}),
        }

class MovimientoStockForm(forms.ModelForm):
    class Meta:
        model = MovimientoStock
        fields = ['producto', 'cantidad', 'tipo_movimiento', 'nota']
        widgets = {
            'producto': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'cantidad': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'tipo_movimiento': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'nota': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'rows': 2}),
        }
        help_texts = {
            'cantidad': 'Positivo para entradas, negativo para salidas',
            'nota': 'Razón del movimiento (opcional)',
        }

class ProductoFilterForm(forms.Form):
    """Formulario para filtrar productos en la lista"""
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(activa=True),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={'class': 'px-3 py-2 border border-gray-300 rounded-md'})
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + list(Producto.ESTADO_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'px-3 py-2 border border-gray-300 rounded-md'})
    )
    busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-md',
            'placeholder': 'Buscar por nombre o código'
        })
    )
