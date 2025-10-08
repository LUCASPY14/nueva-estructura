from django.shortcuts import render

def lista_proveedores(request):
    return render(request, 'proveedores/lista.html', {'title': 'Lista de Proveedores'})
