# lgservice/views.py
from django.shortcuts import redirect

def home(request):
    """
    Redirige a la lista de alumnos (o muestra una plantilla de bienvenida).
    """
    return redirect('alumnos:lista')  # Cambiado de 'alumnos:alumnos_lista' a 'alumnos:lista'
