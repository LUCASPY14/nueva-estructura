from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from .models import Compra, DetalleCompra
from .forms import CompraForm, DetalleCompraFormSet

def es_admin(user):
    return user.is_superuser or user.groups.filter(name='Administradores').exists()

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def compras_lista(request):
    compras = Compra.objects.select_related('proveedor').all().order_by('-fecha')
    return render(request, 'compras/compras_lista.html', {'compras': compras})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
@transaction.atomic
def crear_compra(request):
    if request.method == 'POST':
        form = CompraForm(request.POST)
        formset = DetalleCompraFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            compra = form.save(commit=False)
            compra.total = 0
            compra.save()
            detalles = formset.save(commit=False)
            total = 0
            for detalle in detalles:
                detalle.compra = compra
                producto = detalle.producto
                producto.cantidad += detalle.cantidad
                producto.save()
                detalle.save()
                total += detalle.subtotal()
            compra.total = total
            compra.save()
            messages.success(request, f"Compra #{compra.id} registrada con éxito.")
            return redirect('compras:compras_lista')
    else:
        form = CompraForm()
        formset = DetalleCompraFormSet()
    return render(request, 'compras/crear_editar_compra.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Crear Compra'
    })

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def detalle_compra(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    detalles = compra.detalles.select_related('producto').all()
    return render(request, 'compras/detalle_compra.html', {
        'compra': compra,
        'detalles': detalles
    })

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
@transaction.atomic
def editar_compra(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    detalles_originales = compra.detalles.select_related('producto').all()
    for det in detalles_originales:
        prod = det.producto
        prod.cantidad -= det.cantidad
        prod.save()

    if request.method == 'POST':
        form = CompraForm(request.POST, instance=compra)
        formset = DetalleCompraFormSet(request.POST, instance=compra)
        if form.is_valid() and formset.is_valid():
            compra = form.save(commit=False)
            compra.detalles.all().delete()
            detalles = formset.save(commit=False)
            total = 0
            for detalle in detalles:
                detalle.compra = compra
                producto = detalle.producto
                producto.cantidad += detalle.cantidad
                producto.save()
                detalle.save()
                total += detalle.subtotal()
            compra.total = total
            compra.save()
            messages.success(request, f"Compra #{compra.id} actualizada correctamente.")
            return redirect('compras:compras_lista')
    else:
        form = CompraForm(instance=compra)
        formset = DetalleCompraFormSet(instance=compra)
    return render(request, 'compras/crear_editar_compra.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Editar Compra'
    })

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
@transaction.atomic
def eliminar_compra(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    if request.method == 'POST':
        for det in compra.detalles.select_related('producto').all():
            prod = det.producto
            prod.cantidad -= det.cantidad
            prod.save()
        compra.delete()
        messages.success(request, f"Compra #{pk} eliminada y stock ajustado.")
        return redirect('compras:compras_lista')
    return render(request, 'compras/confirmar_eliminar_compra.html', {'compra': compra})
