from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import UsuarioLG

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class':'border rounded p-2 w-full','placeholder':'Usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class':'border rounded p-2 w-full','placeholder':'Contraseña'}))

class RegistroPadreForm(UserCreationForm):
    class Meta:
        model = UsuarioLG
        fields = ('username','first_name','last_name','email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = 'PADRE'
        if commit: user.save()
        return user