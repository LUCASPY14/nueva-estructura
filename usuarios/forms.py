from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm as DjangoUserChangeForm
from .models import UsuarioLG

# Estilo base de campos input
BASE_INPUT_CLASSES = 'border border-gray-300 rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-green-500'

# Login personalizado visual
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Usuario',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Contraseña',
        })
    )

# Registro de Padre (solo para padres)
class RegistroPadreForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Correo electrónico',
        })
    )
    first_name = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Nombre',
        })
    )
    last_name = forms.CharField(
        label="Apellido",
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Apellido',
        })
    )

    class Meta:
        model = UsuarioLG
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = 'PADRE'
        if commit:
            user.save()
        return user

# Alta de usuario general (para admin)
class UserCreationForm(UserCreationForm):
    tipo = forms.ChoiceField(
        choices=UsuarioLG.ROLES,
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
        label="Nombre",
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Nombre',
        })
    )
    last_name = forms.CharField(
        label="Apellido",
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Apellido',
        })
    )

    class Meta:
        model = UsuarioLG
        fields = ('username', 'first_name', 'last_name', 'email', 'tipo', 'password1', 'password2')

# Edición de usuario general (para admin)
class UserChangeForm(DjangoUserChangeForm):
    password = None  # No mostramos el campo contraseña aquí
    tipo = forms.ChoiceField(
        choices=UsuarioLG.ROLES,
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
        label="Nombre",
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Nombre',
        })
    )
    last_name = forms.CharField(
        label="Apellido",
        widget=forms.TextInput(attrs={
            'class': BASE_INPUT_CLASSES,
            'placeholder': 'Apellido',
        })
    )
    is_active = forms.BooleanField(
        required=False,
        label="Activo",
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-gray-300 text-green-600 focus:ring-green-500'
        })
    )

    class Meta:
        model = UsuarioLG
        fields = ('username', 'first_name', 'last_name', 'email', 'tipo', 'is_active')
