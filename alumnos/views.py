from django.shortcuts import render

def lista_alumnos(request):
    return render(request, 'alumnos/lista.html', {'title': 'Lista de Alumnos'})
