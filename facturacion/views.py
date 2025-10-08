from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from usuarios.decorators import admin_required, admin_or_supervisor_required

@login_required
@admin_or_supervisor_required
def lista_facturas(request):
    return render(request, 'facturacion/lista.html', {'title': 'Lista de Facturas'})

@login_required
@admin_required
def crear_factura(request):
    return render(request, 'facturacion/crear.html', {'title': 'Crear Factura'})

@login_required
def ver_factura(request, pk):
    return render(request, 'facturacion/ver.html', {'title': 'Ver Factura'})

@login_required
@admin_required
def facturacion_electronica(request):
    return render(request, 'facturacion/electronica.html', {'title': 'Facturación Electrónica'})

@login_required
@admin_or_supervisor_required
def reportes_facturacion(request):
    return render(request, 'facturacion/reportes.html', {'title': 'Reportes de Facturación'})
