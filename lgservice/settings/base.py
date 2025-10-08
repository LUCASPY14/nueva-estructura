"""
Base settings to be imported by environment specific settings files
"""
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Import static files settings
from ..static_settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'rest_framework',
    'corsheaders',
    'django_extensions',
    'debug_toolbar',
    'tailwind',
    'theme',
    'django_browser_reload',
    'compressor',
    # Local apps
    'usuarios.apps.UsuariosConfig',
    'alumnos.apps.AlumnosConfig',
    'productos.apps.ProductosConfig',
    'ventas.apps.VentasConfig',
    'proveedores.apps.ProveedoresConfig',
    'compras.apps.ComprasConfig',
    'facturacion.apps.FacturacionConfig',
    'reportes.apps.ReportesConfig',
    'configuracion.apps.ConfiguracionConfig',
]

# Rest of your base settings...