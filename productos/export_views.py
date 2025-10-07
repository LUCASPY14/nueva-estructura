from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from .models import Producto, MovimientoStock
from .exporters import (
    exportar_productos_pdf,
    exportar_productos_excel,
    exportar_movimientos_excel
)

@login_required
@permission_required('productos.view_producto')
def exportar_productos(request):
    """Vista para exportar lista de productos en PDF o Excel"""
    formato = request.GET.get('formato', 'excel')
    
    # Obtener los productos aplicando los filtros actuales
    productos = Producto.objects.all()
    
    # Aplicar filtros si existen
    categoria = request.GET.get('categoria')
    estado = request.GET.get('estado')
    busqueda = request.GET.get('busqueda')
    
    if categoria:
        productos = productos.filter(categoria=categoria)
    if estado:
        productos = productos.filter(estado=estado)
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(codigo__icontains=busqueda) |
            Q(codigo_barras__icontains=busqueda)
        )
    
    # Exportar según el formato solicitado
    if formato == 'pdf':
        return exportar_productos_pdf(productos, request)
    else:  # excel por defecto
        return exportar_productos_excel(productos)

@login_required
@permission_required('productos.view_movimientostock')
def exportar_movimientos(request):
    """Vista para exportar historial de movimientos en Excel"""
    # Obtener los movimientos aplicando los filtros actuales
    movimientos = MovimientoStock.objects.all().select_related('producto', 'usuario')
    
    # Aplicar filtros si existen
    producto_id = request.GET.get('producto')
    tipo = request.GET.get('tipo')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if producto_id:
        movimientos = movimientos.filter(producto_id=producto_id)
    if tipo:
        movimientos = movimientos.filter(tipo_movimiento=tipo)
    if fecha_inicio:
        movimientos = movimientos.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        movimientos = movimientos.filter(fecha__lte=fecha_fin)
    
    return exportar_movimientos_excel(movimientos)