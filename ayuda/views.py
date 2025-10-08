from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def ayuda_view(request):
    return render(request, 'ayuda/ayuda.html', {'title': 'Centro de Ayuda'})

@login_required
def contacto_view(request):
    return render(request, 'ayuda/contacto.html', {'title': 'Contactar Administrador'})
