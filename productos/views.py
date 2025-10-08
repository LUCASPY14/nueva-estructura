from django.shortcuts import render

def lista_productos(request):
    return render(request, 'productos/lista.html', {'title': 'Lista de Productos'})
