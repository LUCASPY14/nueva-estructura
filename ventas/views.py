from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from usuarios.decorators import admin_required, admin_or_cajero_required, admin_or_supervisor_required
from .models import Venta, TurnoCajero, Caja
from productos.models import Producto
from alumnos.models import Alumno

@login_required
@admin_or_supervisor_required
def lista_ventas(request):
    ventas = Venta.objects.all().order_by('-fecha')[:50]
    return render(request, 'ventas/lista.html', {
        'title': 'Lista de Ventas',
        'ventas': ventas
    })

@login_required
@admin_or_cajero_required
def nueva_venta(request):
    productos = Producto.objects.filter(activo=True, stock__gt=0)
    alumnos = Alumno.objects.filter(activo=True)
    return render(request, 'ventas/nueva.html', {
        'title': 'Nueva Venta',
        'productos': productos,
        'alumnos': alumnos
    })

@login_required
def ver_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'ventas/ver.html', {
        'title': 'Ver Venta',
        'venta': venta
    })

@login_required
@admin_or_cajero_required
def punto_venta(request):
    # Verificar si hay turno activo
    turno_activo = TurnoCajero.objects.filter(
        cajero=request.user,
        fecha_cierre__isnull=True
    ).first()
    
    if not turno_activo:
        messages.warning(request, 'Debes abrir un turno antes de usar el punto de venta.')
        return redirect('ventas:abrir_turno')
    
    productos = Producto.objects.filter(activo=True, stock__gt=0)
    categorias = productos.values_list('categoria', flat=True).distinct()
    alumnos = Alumno.objects.filter(activo=True)
    
    return render(request, 'ventas/pos.html', {
        'title': 'Punto de Venta',
        'productos': productos,
        'categorias': categorias,
        'alumnos': alumnos,
        'turno_activo': turno_activo
    })

@login_required
@admin_or_supervisor_required
def reportes_ventas(request):
    hoy = timezone.now().date()
    
    # Estadísticas del día
    ventas_hoy = Venta.objects.filter(fecha__date=hoy)
    estadisticas = {
        'ventas_hoy': ventas_hoy.count(),
        'total_hoy': ventas_hoy.aggregate(Sum('total'))['total__sum'] or 0,
        'alumnos_atendidos': ventas_hoy.values('alumno').distinct().count(),
    }
    
    return render(request, 'ventas/reportes.html', {
        'title': 'Reportes de Ventas',
        'estadisticas': estadisticas
    })

@login_required
@admin_or_cajero_required
def caja_diaria(request):
    return render(request, 'ventas/caja.html', {'title': 'Caja Diaria'})

@login_required
@admin_or_cajero_required
def dashboard_cajero(request):
    """Dashboard principal para cajeros"""
    hoy = timezone.now().date()
    
    # Verificar turno activo
    turno_activo = TurnoCajero.objects.filter(
        cajero=request.user,
        fecha_cierre__isnull=True
    ).first()
    
    # Estadísticas del día
    ventas_hoy = Venta.objects.filter(fecha__date=hoy)
    estadisticas = {
        'ventas_hoy': ventas_hoy.count(),
        'total_hoy': ventas_hoy.aggregate(Sum('total'))['total__sum'] or 0,
        'alumnos_atendidos': ventas_hoy.values('alumno').distinct().count(),
        'ticket_promedio': 0
    }
    
    if estadisticas['ventas_hoy'] > 0:
        estadisticas['ticket_promedio'] = estadisticas['total_hoy'] / estadisticas['ventas_hoy']
    
    # Productos con stock bajo
    productos_stock_bajo = Producto.objects.filter(
        activo=True,
        stock__lte=5,
        stock__gt=0
    ).order_by('stock')
    
    return render(request, 'ventas/dashboard_cajero.html', {
        'title': 'Dashboard Cajero',
        'turno_activo': turno_activo,
        'estadisticas': estadisticas,
        'productos_stock_bajo': productos_stock_bajo,
        'now': timezone.now()
    })

@login_required
@admin_or_cajero_required
def abrir_turno(request):
    """Vista para abrir un turno de caja"""
    # Verificar si ya hay un turno activo
    turno_activo = TurnoCajero.objects.filter(
        cajero=request.user,
        fecha_cierre__isnull=True
    ).first()
    
    if turno_activo:
        messages.info(request, 'Ya tienes un turno activo.')
        return redirect('ventas:dashboard_cajero')
    
    cajas_disponibles = Caja.objects.filter(activa=True)
    
    if request.method == 'POST':
        caja_id = request.POST.get('caja')
        monto_inicial = request.POST.get('monto_inicial', 0)
        observaciones = request.POST.get('observaciones', '')
        
        caja = get_object_or_404(Caja, id=caja_id)
        
        # Crear el turno
        turno = TurnoCajero.objects.create(
            cajero=request.user,
            caja=caja,
            monto_inicial=float(monto_inicial),
            observaciones_apertura=observaciones
        )
        
        messages.success(request, f'Turno abierto en {caja.nombre}')
        return redirect('ventas:dashboard_cajero')
    
    return render(request, 'ventas/abrir_turno.html', {
        'title': 'Abrir Turno',
        'cajas_disponibles': cajas_disponibles
    })

@login_required
@admin_or_cajero_required
def cerrar_turno(request):
    """Vista para cerrar un turno de caja"""
    turno_activo = TurnoCajero.objects.filter(
        cajero=request.user,
        fecha_cierre__isnull=True
    ).first()
    
    if not turno_activo:
        messages.error(request, 'No tienes un turno activo para cerrar.')
        return redirect('ventas:dashboard_cajero')
    
    # Calcular estadísticas del turno
    ventas_turno = Venta.objects.filter(
        usuario=request.user,
        fecha__gte=turno_activo.fecha_inicio
    )
    
    total_ventas = ventas_turno.aggregate(Sum('total'))['total__sum'] or 0
    cantidad_ventas = ventas_turno.count()
    
    if request.method == 'POST':
        # Procesar el cierre
        monto_final = request.POST.get('monto_final', 0)
        observaciones = request.POST.get('observaciones', '')
        
        turno_activo.monto_final = float(monto_final)
        turno_activo.observaciones_cierre = observaciones
        turno_activo.fecha_cierre = timezone.now()
        turno_activo.save()
        
        messages.success(request, 'Turno cerrado correctamente')
        return redirect('ventas:dashboard_cajero')
    
    return render(request, 'ventas/cerrar_turno.html', {
        'title': 'Cerrar Turno',
        'turno_activo': turno_activo,
        'total_ventas': total_ventas,
        'cantidad_ventas': cantidad_ventas,
        'monto_esperado': turno_activo.monto_inicial + total_ventas
    })
