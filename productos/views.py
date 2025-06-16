from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Producto
from .forms import ProductoForm

def es_admin(user):
    return user.is_superuser or user.groups.filter(name='Administradores').exists()

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/listar_productos.html', {'productos': productos})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado correctamente.")
            return redirect('productos:listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/producto_form.html', {'form': form})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect('productos:listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/producto_form.html', {'form': form})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, "Producto eliminado correctamente.")
        return redirect('productos:listar_productos')
    return render(request, 'productos/producto_confirm_delete.html', {'producto': producto})
