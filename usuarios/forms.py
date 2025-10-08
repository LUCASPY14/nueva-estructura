from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

# Estilos base para todos los inputs
BASE_INPUT_CLASSES = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Usuario',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Contraseña',
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

# Registro de padres
class RegistroPadreForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Correo electrónico',
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Nombre',
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Apellido',
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': BASE_INPUT_CLASSES})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo_usuario = 'padre'
        if commit:
            user.save()
        return user

# Alta de usuario general (para admin)
class CustomUserCreationForm(UserCreationForm):
    TIPO_CHOICES = [
        ('administrador', 'Administrador'),
        ('cajero', 'Cajero'),
        ('padre', 'Padre de Familia'),
        ('supervisor', 'Supervisor'),
    ]
    
    tipo_usuario = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': BASE_INPUT_CLASSES})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Correo electrónico',
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Nombre',
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Apellido',
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'tipo_usuario', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': BASE_INPUT_CLASSES})

# Edición de usuario
class CustomUserChangeForm(UserChangeForm):
    TIPO_CHOICES = [
        ('administrador', 'Administrador'),
        ('cajero', 'Cajero'),
        ('padre', 'Padre de Familia'),
        ('supervisor', 'Supervisor'),
    ]
    
    tipo_usuario = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': BASE_INPUT_CLASSES})
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'tipo_usuario', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'class': BASE_INPUT_CLASSES})
        
        # Remover el campo password de la edición normal
        if 'password' in self.fields:
            del self.fields['password']

# Formulario simple para el perfil del usuario
class PerfilForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'last_name': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'email': forms.EmailInput(attrs={'class': BASE_INPUT_CLASSES}),
        }