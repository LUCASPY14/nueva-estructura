from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import MovimientoStock
from .forms import MovimientoStockForm
from productos.models import Producto

def es_admin(user):
    return user.is_superuser or user.groups.filter(name='Administradores').exists()

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def movimientos_stock(request):
    movimientos = MovimientoStock.objects.select_related('producto').order_by('-fecha')
    return render(request, 'stock/movimientos_stock.html', {'movimientos': movimientos})

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def stock_altas(request):
    movimientos = MovimientoStock.objects.filter(tipo='INGRESO').select_related('producto').order_by('-fecha')
    return render(request, 'stock/stock_altas.html', {'movimientos': movimientos})

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def stock_bajas(request):
    movimientos = MovimientoStock.objects.filter(tipo='EGRESO').select_related('producto').order_by('-fecha')
    return render(request, 'stock/stock_bajas.html', {'movimientos': movimientos})

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def crear_movimiento(request):
    if request.method == 'POST':
        form = MovimientoStockForm(request.POST)
        if form.is_valid():
            mov = form.save()
            mov.aplicar()
            messages.success(request, 'Movimiento aplicado correctamente.')
            return redirect('stock:movimientos_stock')
    else:
        form = MovimientoStockForm()
    return render(request, 'stock/movimiento_form.html', {'form': form})

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def eliminar_movimiento(request, pk):
    mov = get_object_or_404(MovimientoStock, pk=pk)
    if request.method == 'POST':
        mov.delete()
        messages.success(request, 'Movimiento eliminado.')
        return redirect('stock:movimientos_stock')
    return render(request, 'stock/confirmar_eliminar_movimiento.html', {'mov': mov})
@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def eliminar_movimiento(request, pk):
    movimiento = get_object_or_404(MovimientoStock, pk=pk)
    if request.method == "POST":
        movimiento.delete()
        messages.success(request, "Movimiento de stock eliminado correctamente.")
        return redirect('stock:movimientos_list')  # Cambiá por tu nombre real de lista
    return render(request, "stock/confirmar_eliminar_movimiento.html", {"movimiento": movimiento})