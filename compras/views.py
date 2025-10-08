from django.shortcuts import render

def lista_compras(request):
    return render(request, 'compras/lista.html', {'title': 'Lista de Compras'})
