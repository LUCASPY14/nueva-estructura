from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from usuarios.decorators import admin_required, admin_or_cajero_required
from .models import Producto

@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/lista.html', {
        'title': 'Lista de Productos',
        'productos': productos
    })

@login_required
@admin_required
def crear_producto(request):
    return render(request, 'productos/crear.html', {'title': 'Crear Producto'})

@login_required
@admin_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'productos/editar.html', {
        'title': 'Editar Producto',
        'producto': producto
    })

@login_required
def ver_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'productos/ver.html', {
        'title': 'Ver Producto',
        'producto': producto
    })

@login_required
@admin_required
def lista_categorias(request):
    return render(request, 'productos/categorias.html', {'title': 'Categorías'})

@login_required
@admin_required
def control_stock(request):
    return render(request, 'productos/stock.html', {'title': 'Control de Stock'})

@login_required
@admin_required
def actualizar_precios(request):
    return render(request, 'productos/precios.html', {'title': 'Actualizar Precios'})
