from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count, Prefetch, F, Sum
from .models import Proveedor
from .forms import ProveedorForm
from productos.models import Producto

@login_required
@permission_required('proveedores.view_proveedor')
def lista_proveedores(request):
    """Vista para listar todos los proveedores con filtros"""
    # Query base con todas las anotaciones y relaciones necesarias
    queryset = Proveedor.objects.select_related().annotate(
        total_productos=Count('productos', distinct=True)
    )
    
    # Aplicar filtros
    busqueda = request.GET.get('busqueda')
    estado = request.GET.get('estado')
    
    filtros = Q()
    if busqueda:
        filtros |= (
            Q(nombre__icontains=busqueda) | 
            Q(nombre_comercial__icontains=busqueda) |
            Q(numero_documento__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )
    
    if estado:
        filtros &= Q(activo=(estado == 'activo'))

    queryset = queryset.filter(filtros)

    # Ordenar por nombre
    queryset = queryset.order_by('nombre')

    # Calcular estadísticas antes de la paginación
    total_queryset = queryset.aggregate(
        total_proveedores=Count('id'),
        proveedores_activos=Count('id', filter=Q(activo=True))
    )

    # Paginación
    paginator = Paginator(queryset, 10)
    page = request.GET.get('page')
    proveedores = paginator.get_page(page)

    # Extraer estadísticas del aggregate
    total_proveedores = total_queryset['total_proveedores']
    proveedores_activos = total_queryset['proveedores_activos']

    context = {
        'proveedores': proveedores,
        'busqueda': busqueda,
        'estado': estado,
        'total_proveedores': total_proveedores,
        'proveedores_activos': proveedores_activos
    }

    return render(request, 'proveedores/lista_proveedores.html', context)

@login_required
@permission_required('proveedores.add_proveedor')
def crear_proveedor(request):
    """Vista para crear un nuevo proveedor"""
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            messages.success(request, f'Proveedor "{proveedor.nombre}" creado exitosamente')
            return redirect('proveedores:lista')
    else:
        form = ProveedorForm()
    
    return render(request, 'proveedores/form_proveedor.html', {
        'form': form,
        'title': 'Nuevo Proveedor'
    })

@login_required
@permission_required('proveedores.change_proveedor')
def editar_proveedor(request, pk):
    """Vista para editar un proveedor existente"""
    proveedor = get_object_or_404(
        Proveedor.objects.prefetch_related(
            Prefetch('productos', queryset=Producto.objects.select_related())
        ),
        pk=pk
    )
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Proveedor "{proveedor.nombre}" actualizado exitosamente')
            return redirect('proveedores:lista')
    else:
        form = ProveedorForm(instance=proveedor)
    
    return render(request, 'proveedores/form_proveedor.html', {
        'form': form,
        'proveedor': proveedor,
        'title': f'Editar: {proveedor.nombre}'
    })

@login_required
@permission_required('proveedores.delete_proveedor')
def eliminar_proveedor(request, pk):
    """Vista para eliminar un proveedor"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    nombre = proveedor.nombre
    
    if request.method == 'POST':
        # Usar transaction.atomic() para asegurar integridad
        with transaction.atomic():
            proveedor.delete()
            messages.success(request, f'Proveedor "{nombre}" eliminado exitosamente')
            return redirect('proveedores:lista')
    
    return render(request, 'proveedores/confirmar_eliminacion.html', {
        'proveedor': proveedor,
        'title': f'Eliminar: {nombre}'
    })

@login_required
@permission_required('proveedores.view_proveedor')
def detalle_proveedor(request, pk):
    """Vista para ver el detalle de un proveedor"""
    # Optimizar consulta con select_related y prefetch_related
    proveedor = get_object_or_404(
        Proveedor.objects.prefetch_related(
            Prefetch(
                'productos',
                queryset=Producto.objects.select_related().annotate(
                    stock_actual=F('stock'),
                    precio_actual=F('precio')
                )
            )
        ),
        pk=pk
    )
    
    # Calcular estadísticas en una sola consulta
    stats = proveedor.productos.aggregate(
        total_productos=Count('id'),
        valor_total=Sum(F('stock') * F('precio')),
        stock_bajo=Count('id', filter=Q(stock__lte=F('stock_minimo')))
    )
    
    context = {
        'proveedor': proveedor,
        'stats': stats,
        'title': proveedor.nombre
    }

    return render(request, 'proveedores/detalle_proveedor.html', context)
