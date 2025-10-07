from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from django.urls import reverse
from django.db.models import Sum, Count, Q, F, Avg, Prefetch
from django.core.cache import cache
from decimal import Decimal
import json
from datetime import datetime, date

# Importaciones corregidas
from .models import Venta, DetalleVenta, PagoVenta, Caja, TurnoCajero, MetodoPago, ReporteCaja
from .forms import VentaForm, DetalleFormSet, PagoFormSet, TurnoCajeroForm
from productos.models import Producto
from alumnos.models import Alumno
from .decorators import require_active_turno, cajero_required
from .serializers import VentaSerializer, ProductoSerializer
from reportes.reports import ReportesVentas, ReportesCaja

# Función auxiliar para verificar permisos
def es_cajero_o_admin(user):
    """Verifica si el usuario es cajero o administrador"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
def dashboard_ventas(request):
    """Dashboard principal del módulo de ventas"""
    hoy = timezone.now().date()
    
    # Consulta base optimizada para ventas del día
    ventas_base = Venta.objects.filter(
        fecha__date=hoy
    ).select_related(
        'turno', 'cliente', 'cajero'
    )
    
    # Obtener estadísticas en una sola consulta
    stats_ventas = ventas_base.filter(
        estado='completada'
    ).aggregate(
        total_ventas=Count('id'),
        monto_total=Sum('total'),
        promedio_venta=Avg('total'),
        total_productos=Sum('items__cantidad'),
        clientes_unicos=Count('cliente', distinct=True)
    )
    
    # Obtener turno activo con sus relaciones
    turno_activo = TurnoCajero.objects.select_related(
        'caja', 'cajero'
    ).filter(
        cajero=request.user,
        activa=True,
        fecha_fin__isnull=True
    ).first()
    
    # Estadísticas de cajas y productos en una sola consulta
    stats_sistema = {
        'cajas_disponibles': Caja.objects.filter(activa=True).count(),
        'productos_activos': Producto.objects.filter(
            estado='activo',
            stock__gt=F('stock_minimo')
        ).count(),
        'productos_bajos': Producto.objects.filter(
            estado='activo',
            stock__lte=F('stock_minimo')
        ).count()
    }
    
    # Ventas por método de pago
    ventas_por_metodo = PagoVenta.objects.filter(
        venta__fecha__date=hoy,
        venta__estado='completada'
    ).values(
        'metodo_pago__nombre'
    ).annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('-total')
    
    # Ventas recientes con datos precargados
    ventas_recientes = ventas_base.filter(
        estado='completada'
    ).prefetch_related(
        'items__producto'
    ).order_by(
        '-fecha'
    )[:10]
    
    # Productos más vendidos hoy
    productos_top = DetalleVenta.objects.filter(
        venta__fecha__date=hoy,
        venta__estado='completada'
    ).values(
        'producto__nombre'
    ).annotate(
        cantidad_total=Sum('cantidad'),
        monto_total=Sum(F('cantidad') * F('precio_unitario'))
    ).order_by('-cantidad_total')[:5]
    
    context = {
        'estadisticas': {
            'turno_activo': turno_activo,
            'ventas_hoy': stats_ventas['total_ventas'] or 0,
            'total_hoy': stats_ventas['monto_total'] or 0,
            'promedio_venta': stats_ventas['promedio_venta'] or 0,
            'total_productos': stats_ventas['total_productos'] or 0,
            'clientes_unicos': stats_ventas['clientes_unicos'] or 0,
            **stats_sistema
        },
        'ventas_por_metodo': ventas_por_metodo,
        'productos_top': productos_top,
        'ventas_recientes': ventas_recientes
    }
    
    if turno_activo:
        # Estadísticas del turno actual
        stats_turno = ventas_base.filter(
            estado='completada',
            turno=turno_activo
        ).aggregate(
            ventas_turno=Count('id'),
            total_turno=Sum('total')
        )
        context['estadisticas'].update({
            'ventas_turno': stats_turno['ventas_turno'] or 0,
            'total_turno': stats_turno['total_turno'] or 0
        })
    
    return render(request, 'ventas/dashboard.html', context)

@login_required
@cajero_required
@require_active_turno
def pos_view(request):
    """Vista principal del punto de venta mejorada"""
    hoy = timezone.now().date()
    cache_key = f'productos_favoritos_{hoy}'
    
    # 1. Obtener turno activo con todas sus relaciones
    turno_activo = TurnoCajero.objects.select_related(
        'caja',
        'cajero'
    ).prefetch_related(
        Prefetch(
            'ventas',
            queryset=Venta.objects.filter(estado='completada')
        )
    ).get(
        cajero=request.user,
        activa=True,
        fecha_fin__isnull=True
    )
    
    # 2. Productos por categoría con optimizaciones
    from productos.models import Categoria
    
    # Subconsulta optimizada para productos
    productos_qs = Producto.objects.filter(
        estado='activo',
        stock__gt=0
    ).select_related(
        'categoria'
    ).prefetch_related(
        'proveedores'
    ).annotate(
        ventas_hoy=Count(
            'detalleventa',
            filter=Q(
                detalleventa__venta__fecha__date=hoy,
                detalleventa__venta__estado='completada'
            )
        )
    )
    
    # Consulta principal de categorías
    categorias = Categoria.objects.prefetch_related(
        Prefetch('productos', queryset=productos_qs)
    ).filter(
        productos__estado='activo',
        productos__stock__gt=0
    ).distinct()
    
    # 3. Productos más vendidos (con caché)
    productos_favoritos = cache.get(cache_key)
    if productos_favoritos is None:
        productos_mas_vendidos = DetalleVenta.objects.filter(
            venta__estado='completada',
            venta__fecha__date=hoy
        ).values(
            'producto'
        ).annotate(
            total_vendidos=Count('id'),
            monto_total=Sum(F('cantidad') * F('precio_unitario'))
        ).order_by(
            '-total_vendidos'
        )[:8]
        
        if productos_mas_vendidos:
            productos_favoritos = productos_qs.filter(
                id__in=[p['producto'] for p in productos_mas_vendidos]
            )
            # Guardar en caché por 1 hora
            cache.set(cache_key, productos_favoritos, 3600)
        else:
            productos_favoritos = []
    
    # 4. Organizar productos por categoría
    productos_por_categoria = {}
    for categoria in categorias:
        productos = list(categoria.productos.all())  # Ya está prefetch_related
        if productos:
            productos_por_categoria[categoria.nombre] = productos
    
    # 5. Productos sin categoría
    productos_sin_categoria = productos_qs.filter(categoria__isnull=True)
    if productos_sin_categoria.exists():
        productos_por_categoria['Sin Categoría'] = list(productos_sin_categoria)
    
    # 6. Estadísticas del turno actual
    stats_turno = {
        'total_ventas': turno_activo.ventas.count(),
        'monto_total': turno_activo.total_ventas,
        'inicio': turno_activo.fecha_inicio,
        'caja': turno_activo.caja.nombre,
    }
    
    # 7. Métodos de pago disponibles
    metodos_pago = MetodoPago.objects.filter(activo=True)
    
    context = {
        'turno_activo': turno_activo,
        'productos_por_categoria': productos_por_categoria,
        'productos_favoritos': productos_favoritos,
        'stats_turno': stats_turno,
        'metodos_pago': metodos_pago,
        'categorias': categorias
    }
    
    return render(request, 'ventas/pos.html', context)
            estado='activo',
            cantidad__gt=0
        )
        productos_favoritos = [
            ProductoSerializer.serialize_producto(p) for p in productos_favoritos
        ]
    
    # Productos por categoría
    for categoria in categorias:
        productos_activos = categoria.productos.filter(
            estado='activo',
            cantidad__gt=0
        ).order_by('nombre')
        
        if productos_activos:
            productos_por_categoria[categoria.nombre] = [
                ProductoSerializer.serialize_producto(p) for p in productos_activos
            ]
    
    # Productos sin categoría
    productos_sin_categoria = Producto.objects.filter(
        estado='activo',
        cantidad__gt=0,
        categoria__isnull=True
    ).order_by('nombre')
    
    if productos_sin_categoria:
        productos_por_categoria['Sin Categoría'] = [
            ProductoSerializer.serialize_producto(p) for p in productos_sin_categoria
        ]
    
    # Obtener métodos de pago con sus configuraciones
    metodos_pago = MetodoPago.objects.filter(activo=True).order_by('nombre')
    metodos_pago_data = []
    for metodo in metodos_pago:
        metodos_pago_data.append({
            'id': metodo.id,
            'nombre': metodo.nombre,
            'icono': metodo.icono or 'fas fa-money-bill',
            'requiere_comprobante': metodo.requiere_comprobante,
            'permite_cambio': metodo.permite_cambio,
            'es_efectivo': metodo.es_efectivo
        })
    
    # Estadísticas del turno actual
    ventas_turno = Venta.objects.filter(
        turno_cajero=turno_activo,
        estado='completada'
    )
    total_turno = ventas_turno.aggregate(total=Sum('total'))['total'] or 0
    cantidad_ventas = ventas_turno.count()
    
    context = {
        'turno': turno_activo,
        'productos_por_categoria': productos_por_categoria,
        'productos_favoritos': productos_favoritos,
        'metodos_pago': metodos_pago_data,
        'estadisticas_turno': {
            'total': float(total_turno),
            'cantidad_ventas': cantidad_ventas,
            'inicio': turno_activo.fecha_inicio.strftime('%H:%M'),
            'caja': turno_activo.caja.nombre
        },
        'configuracion': {
            'permite_descuentos': True,
            'permite_clientes_opcional': True,
            'imprime_automatico': False,
            'moneda': 'ARS',  # Configurar desde settings
            'decimales': 0,  # Configurar desde settings
            'atajos_teclado': True,
            'modo_pantalla_completa': True,
            'confirmar_cantidades': True,
            'busqueda_instantanea': True,
            'sonidos_activos': True
        },
        'atajos_teclado': {
            'buscar': 'Ctrl + F',
            'pagar': 'Ctrl + P',
            'nueva_venta': 'Ctrl + N',
            'cancelar': 'Esc',
            'guardar': 'Ctrl + S',
            'imprimir': 'Ctrl + I'
        }
    }
    return render(request, 'ventas/pos.html', context)

@login_required
def abrir_turno(request):
    """Vista para abrir un turno de cajero"""
    # Verificar que no tenga un turno activo
    turno_existente = TurnoCajero.objects.filter(
        cajero=request.user,
        activa=True,
        fecha_fin__isnull=True
    ).exists()
    
    if turno_existente:
        messages.info(request, 'Ya tienes un turno activo.')
        return redirect('ventas:pos')
    
    if request.method == 'POST':
        form = TurnoCajeroForm(request.POST)
        if form.is_valid():
            try:
                caja = form.cleaned_data['caja']
                monto_inicial = form.cleaned_data['monto_inicial']
                observaciones = form.cleaned_data['observaciones_apertura']
                
                # Verificar que no haya otro turno activo en esta caja
                turno_caja_activo = TurnoCajero.objects.filter(
                    caja=caja,
                    activa=True,
                    fecha_fin__isnull=True
                ).exists()
                
                if turno_caja_activo:
                    messages.error(request, f'Ya hay un turno activo en la {caja}')
                    return render(request, 'ventas/abrir_turno.html', {'form': form})
                
                # Crear nuevo turno
                turno = TurnoCajero.objects.create(
                    cajero=request.user,
                    caja=caja,
                    monto_inicial=monto_inicial,
                    observaciones_apertura=observaciones
                )
                
                messages.success(request, f'Turno abierto exitosamente en {caja}')
                return redirect('ventas:pos')
                
            except Exception as e:
                messages.error(request, f'Error al abrir turno: {str(e)}')
    else:
        form = TurnoCajeroForm()
    
    cajas_disponibles = Caja.objects.filter(activa=True)
    return render(request, 'ventas/abrir_turno.html', {
        'form': form,
        'cajas_disponibles': cajas_disponibles
    })

@login_required
def cerrar_turno(request):
    """Vista para cerrar un turno de cajero"""
    turno = get_object_or_404(
        TurnoCajero,
        cajero=request.user,
        activa=True,
        fecha_fin__isnull=True
    )
    
    if request.method == 'POST':
        monto_final = Decimal(request.POST.get('monto_final', '0'))
        observaciones = request.POST.get('observaciones', '')
        
        turno.cerrar_turno(monto_final, observaciones)
        messages.success(request, 'Turno cerrado exitosamente')
        return redirect('ventas:resumen_turno', turno_id=turno.id)
    
    return render(request, 'ventas/cerrar_turno.html', {'turno': turno})

@login_required
def resumen_turno(request, turno_id):
    """Vista para mostrar resumen de turno cerrado"""
    turno = get_object_or_404(TurnoCajero, id=turno_id, cajero=request.user)
    
    # Obtener resumen de pagos por método
    pagos_por_metodo = PagoVenta.objects.filter(
        venta__turno_cajero=turno
    ).values('metodo').annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('metodo')
    
    context = {
        'turno': turno,
        'ventas': turno.ventas.all().order_by('-fecha'),
        'pagos_por_metodo': pagos_por_metodo,
    }
    return render(request, 'ventas/resumen_turno.html', context)

@login_required
def estado_turno(request):
    """API para obtener estado del turno actual"""
    turno = TurnoCajero.objects.filter(
        cajero=request.user,
        activa=True,
        fecha_fin__isnull=True
    ).first()
    
    if turno:
        data = {
            'turno_activo': True,
            'caja': turno.caja.nombre,
            'numero_caja': turno.caja.numero,
            'fecha_inicio': turno.fecha_inicio.strftime('%H:%M'),
            'total_ventas': float(turno.total_ventas),
            'cantidad_ventas': turno.cantidad_ventas,
        }
    else:
        data = {'turno_activo': False}
    
    return JsonResponse(data)

@login_required
def estadisticas_dashboard(request):
    """API para obtener estadísticas actualizadas del dashboard"""
    hoy = timezone.now().date()
    ventas_hoy = Venta.objects.filter(
        fecha__date=hoy,
        estado='completada'
    )
    
    # Obtener turno activo del usuario
    turno_activo = TurnoCajero.objects.filter(
        cajero=request.user,
        activa=True,
        fecha_fin__isnull=True
    ).first()
    
    # Cálculos de estadísticas
    total_hoy = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0
    cantidad_hoy = ventas_hoy.count()
    
    # Promedio por venta
    promedio_venta = total_hoy / cantidad_hoy if cantidad_hoy > 0 else 0
    
    # Productos con stock bajo
    productos_stock_bajo = Producto.objects.filter(
        cantidad__lte=F('stock_minimo')
    ).count()
    
    # Datos para el gráfico de ventas por hora
    ventas_por_hora = {}
    for hora in range(24):
        ventas_hora = ventas_hoy.filter(
            fecha__hour=hora
        ).aggregate(
            total=Sum('total')
        )['total'] or 0
        ventas_por_hora[str(hora)] = float(ventas_hora)
    
    # Métodos de pago del día
    pagos_por_metodo = PagoVenta.objects.filter(
        venta__fecha__date=hoy,
        venta__estado='completada'
    ).values('metodo__nombre').annotate(
        total=Sum('monto')
    ).order_by('-total')
    
    data = {
        'fecha_hora': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ventas_hoy': cantidad_hoy,
        'total_hoy': float(total_hoy),
        'promedio_venta': float(promedio_venta),
        'productos_stock_bajo': productos_stock_bajo,
        'ventas_por_hora': ventas_por_hora,
        'pagos_por_metodo': [{
            'metodo': p['metodo__nombre'],
            'total': float(p['total'])
        } for p in pagos_por_metodo]
    }
    
    # Agregar datos del turno si está activo
    if turno_activo:
        data.update({
            'ventas_turno': turno_activo.cantidad_ventas,
            'total_turno': float(turno_activo.total_ventas),
            'inicio_turno': turno_activo.fecha_inicio.strftime('%H:%M')
        })
    
    return JsonResponse(data)

@login_required
def nueva_venta(request):
    """Crear una nueva venta"""
    turno_activo = TurnoCajero.objects.filter(
        cajero=request.user,
        activa=True,
        fecha_fin__isnull=True
    ).first()
    
    if not turno_activo:
        return JsonResponse({'error': 'No tienes un turno activo'}, status=400)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                cliente_id = request.POST.get('cliente_id')
                cliente = None
                if cliente_id:
                    cliente = Alumno.objects.get(id=cliente_id)
                
                venta = Venta.objects.create(
                    cajero=request.user,
                    turno_cajero=turno_activo,
                    cliente=cliente
                )
                
                return JsonResponse({
                    'success': True,
                    'venta_id': venta.id,
                    'numero_venta': venta.numero_venta
                })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def detalle_venta(request, venta_id):
    """Ver detalle de una venta"""
    venta = get_object_or_404(Venta, id=venta_id)
    
    # Verificar permisos
    if venta.cajero != request.user and not request.user.is_staff:
        messages.error(request, 'No tienes permisos para ver esta venta')
        return redirect('ventas:dashboard')
    
    return render(request, 'ventas/detalle_venta.html', {'venta': venta})

@login_required
def cancelar_venta(request, venta_id):
    """Cancelar una venta"""
    venta = get_object_or_404(Venta, id=venta_id)
    
    if venta.cajero != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        try:
            venta.cancelar_venta(motivo)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def imprimir_factura(request, venta_id):
    """Generar factura para impresión"""
    venta = get_object_or_404(Venta, id=venta_id, estado='completada')
    
    # Verificar permisos
    if venta.cajero != request.user and not request.user.is_staff:
        messages.error(request, 'No tienes permisos para imprimir esta factura')
        return redirect('ventas:dashboard')
    
    return render(request, 'ventas/factura.html', {
        'venta': venta,
        'empresa': 'Tu Empresa',  # Configurar desde settings
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def reportes_ventas(request):
    """Vista de reportes de ventas"""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    caja_id = request.GET.get('caja')
    
    if not fecha_inicio:
        fecha_inicio = date.today()
    if not fecha_fin:
        fecha_fin = date.today()
    
    ventas = Venta.objects.filter(
        fecha__date__gte=fecha_inicio,
        fecha__date__lte=fecha_fin,
        estado='completada'
    )
    
    if caja_id:
        ventas = ventas.filter(turno_cajero__caja_id=caja_id)
    
    resumen = ventas.aggregate(
        total_ventas=Sum('total'),
        cantidad_ventas=Count('id')
    )
    
    context = {
        'ventas': ventas.order_by('-fecha'),
        'resumen': resumen,
        'cajas': Caja.objects.filter(activa=True),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'caja_id': caja_id,
    }
    
    return render(request, 'ventas/reportes.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def reporte_caja(request, caja_id):
    """Reporte específico de una caja"""
    caja = get_object_or_404(Caja, id=caja_id)
    fecha = request.GET.get('fecha', date.today())
    
    turnos = TurnoCajero.objects.filter(
        caja=caja,
        fecha_inicio__date=fecha
    ).order_by('fecha_inicio')
    
    return render(request, 'ventas/reporte_caja.html', {
        'caja': caja,
        'turnos': turnos,
        'fecha': fecha,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def reporte_cajero(request, cajero_id):
    """Reporte específico de un cajero"""
    from usuarios.models import UsuarioLG
    cajero = get_object_or_404(UsuarioLG, id=cajero_id)
    fecha = request.GET.get('fecha', date.today())
    
    turnos = TurnoCajero.objects.filter(
        cajero=cajero,
        fecha_inicio__date=fecha
    ).order_by('fecha_inicio')
    
    return render(request, 'ventas/reporte_cajero.html', {
        'cajero': cajero,
        'turnos': turnos,
        'fecha': fecha,
    })

@login_required
def reporte_diario(request):
    """Vista para el reporte diario de ventas"""
    fecha_str = request.GET.get('fecha', timezone.now().date().strftime('%Y-%m-%d'))
    caja_id = request.GET.get('caja')
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        fecha = timezone.now().date()
    
    caja = None
    if caja_id:
        try:
            caja = Caja.objects.get(id=caja_id)
        except Caja.DoesNotExist:
            pass
    
    reporte = ReportesVentas.reporte_diario(fecha, caja)
    cajas = Caja.objects.filter(activa=True)
    
    return render(request, 'ventas/reportes/diario.html', {
        'reporte': reporte,
        'cajas': cajas,
        'fecha_seleccionada': fecha_str
    })

@login_required
def reporte_turno(request, turno_id):
    """Vista para el reporte de turno"""
    reporte = ReportesVentas.reporte_turno(turno_id)
    
    if not reporte:
        return render(request, 'ventas/reportes/error.html', {
            'mensaje': 'Turno no encontrado'
        })
    
    return render(request, 'ventas/reportes/turno.html', {
        'reporte': reporte
    })

@login_required
def datos_ventas_en_vivo(request):
    """API para obtener datos de ventas en tiempo real"""
    hoy = timezone.now().date()
    hora_actual = timezone.now().time()
    
    # Ventas del día actual
    ventas_hoy = Venta.objects.filter(
        fecha__date=hoy,
        estado='completada'
    )
    
    # Datos de resumen
    total_ventas = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0
    cantidad_ventas = ventas_hoy.count()
    promedio_venta = total_ventas / cantidad_ventas if cantidad_ventas > 0 else 0
    
    # Datos por hora
    ventas_por_hora = []
    for hora in range(hora_actual.hour + 1):
        ventas_hora = ventas_hoy.filter(fecha__hour=hora)
        total_hora = ventas_hora.aggregate(total=Sum('total'))['total'] or 0
        cantidad_hora = ventas_hora.count()
        ventas_por_hora.append({
            'hora': f'{hora:02d}:00',
            'total': float(total_hora),
            'cantidad': cantidad_hora
        })
    
    # Productos más vendidos
    productos_vendidos = DetalleVenta.objects.filter(
        venta__fecha__date=hoy,
        venta__estado='completada'
    ).values('producto__nombre').annotate(
        total_vendido=Sum('cantidad'),
        total_dinero=Sum('subtotal')
    ).order_by('-total_vendido')[:5]
    
    # Métodos de pago
    pagos_por_metodo = PagoVenta.objects.filter(
        venta__fecha__date=hoy,
        venta__estado='completada'
    ).values('metodo__nombre').annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('-total')
    
    # Últimas ventas
    ultimas_ventas = []
    for venta in ventas_hoy.order_by('-fecha')[:5]:
        ultimas_ventas.append({
            'id': venta.id,
            'hora': venta.fecha.strftime('%H:%M'),
            'total': float(venta.total),
            'items': venta.detalleventa_set.count(),
            'estado': venta.get_estado_display(),
            'cliente': str(venta.cliente) if venta.cliente else 'Cliente General'
        })
    
    return JsonResponse({
        'resumen': {
            'total_ventas': float(total_ventas),
            'cantidad_ventas': cantidad_ventas,
            'promedio_venta': float(promedio_venta),
            'fecha_hora': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'ventas_por_hora': ventas_por_hora,
        'productos_mas_vendidos': list(productos_vendidos),
        'pagos_por_metodo': list(pagos_por_metodo),
        'ultimas_ventas': ultimas_ventas
    })

@login_required
def datos_ventas_por_periodo(request, periodo):
    """API para obtener datos de ventas por período (hoy, semana, mes)"""
    hoy = timezone.now().date()
    hora_actual = timezone.now().time()
    
    if periodo == 'hoy':
        fecha_inicio = hoy
        fecha_fin = hoy
        agrupar_por = 'hora'
    elif periodo == 'semana':
        fecha_inicio = hoy - timezone.timedelta(days=7)
        fecha_fin = hoy
        agrupar_por = 'dia'
    elif periodo == 'mes':
        fecha_inicio = hoy - timezone.timedelta(days=30)
        fecha_fin = hoy
        agrupar_por = 'dia'
    else:
        return JsonResponse({'error': 'Período no válido'}, status=400)
    
    # Query base para ventas completadas en el período
    ventas = Venta.objects.filter(
        fecha__date__gte=fecha_inicio,
        fecha__date__lte=fecha_fin,
        estado='completada'
    )
    
    # Preparar datos según agrupación
    datos = []
    labels = []
    
    if agrupar_por == 'hora':
        # Datos por hora para el día actual
        for hora in range(24):
            if hora > hora_actual.hour:
                continue
                
            ventas_hora = ventas.filter(fecha__hour=hora)
            total_hora = ventas_hora.aggregate(total=Sum('total'))['total'] or 0
            
            datos.append(float(total_hora))
            labels.append(f'{hora:02d}:00')
    else:
        # Datos por día
        fecha = fecha_inicio
        while fecha <= fecha_fin:
            ventas_dia = ventas.filter(fecha__date=fecha)
            total_dia = ventas_dia.aggregate(total=Sum('total'))['total'] or 0
            
            datos.append(float(total_dia))
            labels.append(fecha.strftime('%d/%m'))
            
            fecha += timezone.timedelta(days=1)
    
    return JsonResponse({
        'labels': labels,
        'datos': datos,
        'periodo': periodo,
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d')
    })

@login_required
def api_reporte_cajas(request):
    """API para obtener datos de cajas en JSON"""
    fecha_str = request.GET.get('fecha', timezone.now().date().strftime('%Y-%m-%d'))
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        fecha = timezone.now().date()
    
    reporte = ReportesCaja.reporte_cajas_diario(fecha)
    
    return JsonResponse({
        'fecha': fecha.strftime('%Y-%m-%d'),
        'cajas': [
            {
                'numero': caja_data['caja'].numero,
                'nombre': caja_data['caja'].nombre,
                'total_ventas': float(caja_data['total_ventas']),
                'cantidad_ventas': caja_data['cantidad_ventas'],
                'turnos_activos': caja_data['turnos_activos']
            }
            for caja_data in reporte['cajas']
        ]
    })
