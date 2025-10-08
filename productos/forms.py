from django import forms
from .models import Producto, Categoria, MovimientoStock

class ProductoForm(forms.ModelForm):
    """Formulario para crear y editar productos"""
    
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'descripcion', 
            'categoria',
            'codigo',
            'precio',
            'cantidad',
            'cantidad_minima',
            'activo',
            'imagen',
            'peso'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del producto'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código del producto'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'cantidad_minima': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.filter(activa=True)
        self.fields['descripcion'].required = False
        self.fields['imagen'].required = False
        self.fields['peso'].required = False

class CategoriaForm(forms.ModelForm):
    """Formulario para crear y editar categorías"""
    
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la categoría'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descripcion'].required = False

class MovimientoStockForm(forms.ModelForm):
    """Formulario para registrar movimientos de stock"""
    
    class Meta:
        model = MovimientoStock
        fields = ['producto', 'tipo', 'cantidad', 'motivo']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'motivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Motivo del movimiento'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(activo=True)

class BuscarProductoForm(forms.Form):
    """Formulario para buscar productos"""
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, código o categoría...'
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(activa=True),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
