from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import MovimientoStock
from .forms import MovimientoStockForm
from productos.models import Producto

# Solo Administradores pueden gestionar stock

def es_admin(user):
    return user.groups.filter(name='Administradores').exists()

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def stock_list(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'stock/stock_list.html', {'productos': productos})
def stock_altas(request):
    """
    Lista solo los movimientos de tipo INGRESO (altas de stock).
    """
    movimientos = MovimientoStock.objects.filter(tipo='INGRESO').select_related('producto').order_by('-fecha')
    return render(request, 'stock/stock_altas.html', {'movimientos': movimientos})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def stock_bajas(request):
    """
    Lista solo los movimientos de tipo EGRESO (bajas de stock).
    """
    movimientos = MovimientoStock.objects.filter(tipo='EGRESO').select_related('producto').order_by('-fecha')
    return render(request, 'stock/stock_bajas.html', {'movimientos': movimientos})
@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def movimientos_list(request):
    movimientos = MovimientoStock.objects.select_related('producto').all()
    return render(request, 'stock/stock_list.html', {'movimientos': movimientos})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def crear_movimiento(request):
    if request.method == 'POST':
        form = MovimientoStockForm(request.POST)
        if form.is_valid():
            mov = form.save()
            mov.aplicar()
            messages.success(request, 'Movimiento aplicado correctamente.')
            return redirect('stock:movimientos_list')
    else:
        form = MovimientoStockForm()
    return render(request, 'stock/movimiento_form.html', {'form': form})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def confirmar_eliminar(request, pk):
    mov = get_object_or_404(MovimientoStock, pk=pk)
    if request.method == 'POST':
        mov.delete()
        messages.success(request, 'Movimiento eliminado.')
        return redirect('stock:movimientos_list')
    return render(request, 'stock/confirmar_eliminar_movimiento.html', {'mov': mov})