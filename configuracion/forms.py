from django import forms
from .models import ConfiguracionSistema

class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionSistema
        fields = '__all__'
        widgets = {
            'nombre_sistema': forms.TextInput(attrs={'class': 'form-input'}),
            'moneda': forms.TextInput(attrs={'class': 'form-input'}),
            'limite_credito': forms.NumberInput(attrs={'class': 'form-input'}),
            'horario_atencion': forms.TextInput(attrs={'class': 'form-input'}),
            'color_principal': forms.TextInput(attrs={'type': 'color', 'class': 'form-input'}),
        }
