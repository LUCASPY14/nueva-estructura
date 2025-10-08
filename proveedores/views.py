from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from usuarios.decorators import admin_required

@login_required
@admin_required
def lista_proveedores(request):
    return render(request, 'proveedores/lista.html', {'title': 'Lista de Proveedores'})

@login_required
@admin_required
def crear_proveedor(request):
    return render(request, 'proveedores/crear.html', {'title': 'Crear Proveedor'})

@login_required
@admin_required
def editar_proveedor(request, pk):
    return render(request, 'proveedores/editar.html', {'title': 'Editar Proveedor'})

@login_required
@admin_required
def ver_proveedor(request, pk):
    return render(request, 'proveedores/ver.html', {'title': 'Ver Proveedor'})

@login_required
@admin_required
def gestionar_contactos(request):
    return render(request, 'proveedores/contactos.html', {'title': 'Gestionar Contactos'})
