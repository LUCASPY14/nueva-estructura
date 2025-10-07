from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import models
from django.db.models import (
    Q, Sum, Count, F, Prefetch, ExpressionWrapper, DateTimeField,
    Avg, Subquery, OuterRef
)
from django.db.models.functions import ExtractDay, Now
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache
from .models import Producto, Categoria, MovimientoStock, HistorialPrecios
from .forms import ProductoForm, CategoriaForm, MovimientoStockForm, ProductoFilterForm
from proveedores.models import Proveedor
from ventas.models import DetalleVenta

@login_required
def lista_productos(request):
    """
    Vista para listar todos los productos con filtros y estadísticas.
    
    Esta vista implementa:
    - Caché de estadísticas para reducir carga en DB
    - Consultas optimizadas con select_related y prefetch_related
    - Filtros dinámicos
    - Paginación eficiente
    - Ordenamiento personalizable
    """
    # Cache keys específicos por usuario y filtros
    user_id = request.user.id
    filter_params = frozenset(request.GET.items())
    cache_key_stats = f'productos_stats_{user_id}_{timezone.now().date()}'
    cache_key_filtros = f'productos_filtros_{user_id}_{hash(filter_params)}'
    
    # Obtener estadísticas del cache o calcularlas
    stats = cache.get(cache_key_stats)
    if stats is None:
        # Usamos anotaciones para cálculos eficientes
        productos_base = Producto.objects.all()
        stats = productos_base.aggregate(
            total_productos=Count('id'),
            productos_bajo_stock=Count(
                'id',
                filter=Q(cantidad__lte=F('cantidad_minima'))
            ),
            productos_activos=Count(
                'id',
                filter=Q(estado='activo')
            ),
            valor_total_inventario=Sum(
                ExpressionWrapper(
                    F('cantidad') * F('precio_costo'),
                    output_field=models.DecimalField()
                )
            ),
            productos_sin_stock=Count(
                'id',
                filter=Q(cantidad=0)
            ),
            promedio_precio_venta=Avg('precio_venta'),
        )
        cache.set(cache_key_stats, stats, 3600)  # Cache por 1 hora
    
    # Query base con optimizaciones
    productos = cache.get(cache_key_filtros)
    if productos is None:
        productos = Producto.objects.select_related(
            'categoria',
            'proveedor_principal'
        ).prefetch_related(
            Prefetch(
                'proveedores_alternativos',
                queryset=Proveedor.objects.only('id', 'nombre', 'activo')
                .filter(activo=True)
            ),
            Prefetch(
                'movimientos',
                queryset=MovimientoStock.objects.filter(
                    fecha__gte=timezone.now().date()
                ).select_related('usuario')
                .only('id', 'fecha', 'cantidad', 'tipo_movimiento', 'usuario__username')
                .order_by('-fecha')[:5]
            )
        ).annotate(
            ventas_hoy=Count(
                'detalleventa',
                filter=Q(
                    detalleventa__venta__fecha__date=timezone.now().date(),
                    detalleventa__venta__estado='completada'
                )
            ),
            dias_sin_movimiento=ExtractDay(Now() - F('fecha_ultimo_pedido')),
            ultimo_precio_compra=Subquery(
                HistorialPrecios.objects.filter(
                    producto=OuterRef('pk')
                ).order_by('-fecha')
                .values('precio')[:1]
            ),
            margen_ganancia=ExpressionWrapper(
                (F('precio_venta') - F('precio_costo')) / F('precio_costo') * 100,
                output_field=models.DecimalField()
            )
        ).only(
            'id', 'codigo', 'nombre', 'estado', 'cantidad', 
            'cantidad_minima', 'precio_venta', 'precio_costo'
        )
    
    # Aplicar filtros si el formulario es válido
    filter_form = ProductoFilterForm(request.GET)
    if filter_form.is_valid():
        filtros = Q()
        
        categoria = filter_form.cleaned_data.get('categoria')
        estado = filter_form.cleaned_data.get('estado')
        busqueda = filter_form.cleaned_data.get('busqueda')
        
        if categoria:
            filtros &= Q(categoria=categoria)
        if estado:
            filtros &= Q(estado=estado)
        if busqueda:
            filtros |= (
                Q(nombre__icontains=busqueda) | 
                Q(codigo__icontains=busqueda) | 
                Q(codigo_barras__icontains=busqueda)
            )
        
        productos = productos.filter(filtros)
    
    # Ordenamiento
    orden = request.GET.get('orden', 'nombre')
    if orden.startswith('-'):
        productos = productos.order_by(F(orden[1:]).desc(nulls_last=True))
    else:
        productos = productos.order_by(F(orden).asc(nulls_last=True))
    
    # Paginación
    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'productos': page_obj,
        'filter_form': filter_form,
        'stats': stats,
        'title': 'Lista de Productos',
        'orden_actual': orden
    }
    
    return render(request, 'productos/lista_productos.html', context)

@login_required
@permission_required('productos.add_producto', raise_exception=True)
def crear_producto(request):
    """Vista para crear un nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f"Producto {producto.nombre} creado exitosamente")
            return redirect('productos:lista_productos')
    else:
        form = ProductoForm()
    
    return render(request, 'productos/crear_producto.html', {
        'form': form,
        'title': 'Crear Producto',
    })

@login_required
@permission_required('productos.change_producto', raise_exception=True)
def editar_producto(request, pk):
    """Vista para editar un producto existente"""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Producto {producto.nombre} actualizado exitosamente")
            return redirect('productos:lista_productos')
    else:
        form = ProductoForm(instance=producto)
    
    # Incluir historial de movimientos
    movimientos = producto.movimientos.all()[:10]  # Últimos 10 movimientos
    
    return render(request, 'productos/editar_producto.html', {
        'form': form,
        'producto': producto,
        'movimientos': movimientos,
        'title': f'Editar: {producto.nombre}',
    })

@login_required
@permission_required('productos.view_producto', raise_exception=True)
def detalle_producto(request, pk):
    """Vista para ver el detalle de un producto"""
    # Obtener producto con todas sus relaciones y datos necesarios
    producto = get_object_or_404(
        Producto.objects.select_related(
            'categoria',
            'proveedor_principal'
        ).prefetch_related(
            Prefetch(
                'proveedores_alternativos',
                queryset=Proveedor.objects.only('id', 'nombre', 'activo')
            ),
            Prefetch(
                'movimientos',
                queryset=MovimientoStock.objects.select_related('usuario').order_by('-fecha')[:15]
            ),
            Prefetch(
                'detalleventa_set',
                queryset=DetalleVenta.objects.select_related('venta').filter(
                    venta__estado='completada',
                    venta__fecha__gte=timezone.now().date() - timezone.timedelta(days=30)
                )
            )
        ).annotate(
            ventas_mes=Count(
                'detalleventa',
                filter=Q(
                    detalleventa__venta__estado='completada',
                    detalleventa__venta__fecha__gte=timezone.now().date() - timezone.timedelta(days=30)
                )
            ),
            valor_inventario=ExpressionWrapper(
                F('cantidad') * F('precio_costo'),
                output_field=models.DecimalField()
            ),
            dias_sin_movimiento=ExtractDay(Now() - F('fecha_ultimo_pedido')),
            margen_promedio=ExpressionWrapper(
                (F('precio_venta') - F('precio_costo')) / F('precio_costo') * 100,
                output_field=models.DecimalField()
            )
        ),
        pk=pk
    )
    
    # Calcular estadísticas de ventas
    ventas_stats = producto.detalleventa_set.aggregate(
        total_vendido=Sum('cantidad'),
        total_ingresos=Sum(F('cantidad') * F('precio_unitario')),
        promedio_unidades=Avg('cantidad')
    )
    
    # Obtener proveedores alternativos con sus últimos precios
    proveedores_precios = producto.productoproveedor_set.select_related(
        'proveedor'
    ).order_by(
        'proveedor__nombre'
    ).annotate(
        ultimo_precio=Subquery(
            HistorialPrecios.objects.filter(
                producto=OuterRef('producto'),
                proveedor=OuterRef('proveedor')
            ).order_by('-fecha').values('precio')[:1]
        )
    )
    
    context = {
        'producto': producto,
        'ventas_stats': ventas_stats,
        'proveedores_precios': proveedores_precios,
        'title': producto.nombre
    }
    
    return render(request, 'productos/detalle_producto.html', context)
        'producto': producto,
        'movimientos': movimientos
    })

@login_required
def stock_alerts_api(request):
    """API para obtener alertas de stock"""
    from .serializers import StockAlertsSerializer
    
    alertas = StockAlertsSerializer.get_stock_alerts()
    
    return JsonResponse({
        'alertas': alertas,
        'fecha_actualizacion': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        'resumen': {
            'total_alertas': len(alertas),
            'agotados': len([a for a in alertas if a['estado'] == 'agotado']),
            'criticos': len([a for a in alertas if a['estado'] == 'critico']),
            'bajos': len([a for a in alertas if a['estado'] == 'bajo']),
            'advertencias': len([a for a in alertas if a['estado'] == 'advertencia'])
        }
    })
        
@login_required
def stock_alerts_api(request):
    """API para obtener alertas de stock"""
    from .serializers import StockAlertsSerializer
    
    alertas = StockAlertsSerializer.get_stock_alerts()
    
    return JsonResponse({
        'alertas': alertas,
        'fecha_actualizacion': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        'resumen': {
            'total_alertas': len(alertas),
            'agotados': len([a for a in alertas if a['estado'] == 'agotado']),
            'criticos': len([a for a in alertas if a['estado'] == 'critico']),
            'bajos': len([a for a in alertas if a['estado'] == 'bajo']),
            'advertencias': len([a for a in alertas if a['estado'] == 'advertencia'])
        }
    })

@login_required
@permission_required('productos.delete_producto', raise_exception=True)
def eliminar_producto(request, pk):
    """Vista para eliminar un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f"Producto '{nombre}' eliminado exitosamente")
        return redirect('productos:lista_productos')
    
    return render(request, 'productos/confirmar_eliminacion.html', {
        'producto': producto,
        'title': f'Eliminar: {producto.nombre}',
    })

@login_required
@permission_required('productos.add_movimientostock', raise_exception=True)
def registrar_movimiento(request):
    """Vista para registrar un movimiento de stock"""
    if request.method == 'POST':
        form = MovimientoStockForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            movimiento.save()  # Esto activará el método save() del modelo que actualizará el stock
            
            messages.success(
                request, 
                f"Movimiento de {movimiento.get_tipo_movimiento_display()} registrado para {movimiento.producto.nombre}"
            )
            return redirect('productos:lista_productos')
    else:
        form = MovimientoStockForm()
    
    return render(request, 'productos/registrar_movimiento.html', {
        'form': form,
        'title': 'Registrar Movimiento de Stock',
    })

@login_required
@permission_required('productos.view_movimientostock', raise_exception=True)
def historial_movimientos(request):
    """Vista para ver el historial completo de movimientos"""
    movimientos = MovimientoStock.objects.all().select_related('producto', 'usuario')
    
    # Filtros
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
    
    # Paginación
    paginator = Paginator(movimientos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'productos/historial_movimientos.html', {
        'movimientos': page_obj,
        'title': 'Historial de Movimientos',
        'productos': Producto.objects.all(),  # Para el filtro
    })

# Vistas para Categorías
@login_required
@permission_required('productos.view_categoria', raise_exception=True)
def lista_categorias(request):
    """Vista para listar todas las categorías"""
    categorias = Categoria.objects.all()
    
    # Estadísticas
    for categoria in categorias:
        categoria.productos_count = categoria.productos.count()
    
    return render(request, 'productos/lista_categorias.html', {
        'categorias': categorias,
        'title': 'Categorías de Productos',
    })

@login_required
@permission_required('productos.add_categoria', raise_exception=True)
def crear_categoria(request):
    """Vista para crear una nueva categoría"""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f"Categoría {categoria.nombre} creada exitosamente")
            return redirect('productos:lista_categorias')
    else:
        form = CategoriaForm()
    
    return render(request, 'productos/crear_categoria.html', {
        'form': form,
        'title': 'Crear Categoría',
    })

@login_required
@permission_required('productos.change_categoria', raise_exception=True)
def editar_categoria(request, pk):
    """Vista para editar una categoría existente"""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f"Categoría {categoria.nombre} actualizada exitosamente")
            return redirect('productos:lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'productos/editar_categoria.html', {
        'form': form,
        'categoria': categoria,
        'title': f'Editar: {categoria.nombre}',
    })

@login_required
def productos_dashboard(request):
    """Dashboard de productos con estadísticas y alertas"""
    # Resumen general
    total_productos = Producto.objects.count()
    productos_activos = Producto.objects.filter(estado='activo').count()
    valor_inventario = Producto.objects.filter(estado='activo').aggregate(
        total=Sum(F('cantidad') * F('precio_venta'))
    )['total'] or 0
    
    # Productos con bajo stock
    bajo_stock = Producto.objects.filter(
        cantidad__lte=F('cantidad_minima'),
        estado='activo'
    ).order_by('cantidad')[:5]
    
    # Productos más vendidos (basado en movimientos de salida)
    # Esto asume que tienes relación con ventas o movimientos
    top_vendidos = MovimientoStock.objects.filter(
        tipo_movimiento='salida'
    ).values('producto__nombre').annotate(
        total=Sum('cantidad')
    ).order_by('-total')[:5]
    
    # Productos por categoría
    por_categoria = Categoria.objects.annotate(
        count=Count('productos')
    ).values('nombre', 'count').order_by('-count')
    
    return render(request, 'productos/dashboard.html', {
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'valor_inventario': valor_inventario,
        'bajo_stock': bajo_stock,
        'top_vendidos': top_vendidos,
        'por_categoria': por_categoria,
        'title': 'Dashboard de Productos',
    })
