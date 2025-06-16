from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm as DjangoUserChangeForm
from .models import UsuarioLG

# Login personalizado visual
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Usuario',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Contraseña',
        })
    )

# Registro de Padre (solo para padres)
class RegistroPadreForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Correo electrónico',
        })
    )
    first_name = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Nombre',
        })
    )
    last_name = forms.CharField(
        label="Apellido",
        widget=forms.TextInput(attrs={
            'class': 'border rounded p-2 w-full',
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
        widget=forms.Select(attrs={'class': 'border rounded p-2 w-full'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Correo electrónico',
        })
    )
    first_name = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Nombre',
        })
    )
    last_name = forms.CharField(
        label="Apellido",
        widget=forms.TextInput(attrs={
            'class': 'border rounded p-2 w-full',
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
        widget=forms.Select(attrs={'class': 'border rounded p-2 w-full'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Correo electrónico',
        })
    )
    first_name = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Nombre',
        })
    )
    last_name = forms.CharField(
        label="Apellido",
        widget=forms.TextInput(attrs={
            'class': 'border rounded p-2 w-full',
            'placeholder': 'Apellido',
        })
    )
    is_active = forms.BooleanField(
        required=False,
        label="Activo",
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox rounded text-blue-600'})
    )

    class Meta:
        model = UsuarioLG
        fields = ('username', 'first_name', 'last_name', 'email', 'tipo', 'is_active')

