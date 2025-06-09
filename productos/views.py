# productos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Producto, Proveedor
from .forms import ProductoForm, ProveedorForm

def es_admin(user):
    return user.groups.filter(name='Administradores').exists()

# — VISTAS DE PRODUCTOS — #

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def productos_lista(request):
    productos = Producto.objects.select_related('proveedor').all().order_by('nombre')
    return render(request, 'productos/productos_lista.html', {'productos': productos})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado exitosamente.")
            return redirect('productos:listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/crear_editar_producto.html', {
        'form': form,
        'titulo': 'Crear Producto'
    })

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto modificado exitosamente.")
            return redirect('productos:listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/crear_editar_producto.html', {
        'form': form,
        'titulo': 'Editar Producto'
    })

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, "Producto eliminado correctamente.")
        return redirect('productos:listar_productos')
    return render(request, 'productos/confirmar_eliminar_producto.html', {'producto': producto})

# — VISTAS DE PROVEEDOR (opcionales) — #

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def proveedores_lista(request):
    proveedores = Proveedor.objects.all().order_by('nombre')
    return render(request, 'productos/proveedores_lista.html', {'proveedores': proveedores})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor creado exitosamente.")
            return redirect('productos:listar_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'productos/crear_editar_proveedor.html', {
        'form': form,
        'titulo': 'Crear Proveedor'
    })

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor modificado exitosamente.")
            return redirect('productos:listar_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'productos/crear_editar_proveedor.html', {
        'form': form,
        'titulo': 'Editar Proveedor'
    })

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, "Proveedor eliminado.")
        return redirect('productos:listar_proveedores')
    return render(request, 'productos/confirmar_eliminar_proveedor.html', {'proveedor': proveedor})
