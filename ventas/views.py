from django.shortcuts import render

def lista_ventas(request):
    return render(request, 'ventas/lista.html', {'title': 'Lista de Ventas'})
