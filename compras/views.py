from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from usuarios.decorators import admin_required

@login_required
@admin_required
def lista_compras(request):
    return render(request, 'compras/lista.html', {'title': 'Lista de Compras'})

@login_required
@admin_required
def nueva_compra(request):
    return render(request, 'compras/nueva.html', {'title': 'Nueva Compra'})

@login_required
@admin_required
def ver_compra(request, pk):
    return render(request, 'compras/ver.html', {'title': 'Ver Compra'})

@login_required
@admin_required
def ordenes_compra(request):
    return render(request, 'compras/ordenes.html', {'title': 'Órdenes de Compra'})

@login_required
@admin_required
def recepcion_mercancia(request):
    return render(request, 'compras/recepcion.html', {'title': 'Recepción de Mercancía'})
