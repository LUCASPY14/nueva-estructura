from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Producto
from .forms import ProductoForm

# Listar productos
def listar_productos(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'productos/producto_lista.html', {
        'productos': productos,
        'titulo': 'Lista de productos'
    })

# Crear producto
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado correctamente.')
            return redirect('productos:listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/producto_form.html', {
        'form': form,
        'titulo': 'Nuevo Producto'
    })

# Editar producto
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('productos:listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/producto_form.html', {
        'form': form,
        'titulo': 'Editar Producto'
    })

# Eliminar producto
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente.')
        return redirect('productos:listar_productos')
    return render(request, 'productos/producto_confirmar_eliminar.html', {
        'producto': producto,
        'titulo': 'Eliminar Producto'
    })
