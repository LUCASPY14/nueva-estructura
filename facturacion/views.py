from django.shortcuts import render

def lista_facturas(request):
    return render(request, 'facturacion/lista.html', {'title': 'Lista de Facturas'})
