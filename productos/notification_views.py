from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import models
from .models import Producto

@login_required
def lista_notificaciones(request):
    """Vista para mostrar todas las notificaciones del usuario"""
    notificaciones = StockNotification.objects.filter(
        destinatarios=request.user
    ).select_related('producto')
    
    context = {
        'notificaciones': notificaciones,
        'title': 'Notificaciones de Stock'
    }
    
    if request.headers.get('HX-Request'):
        # Si es una petición HTMX, devolver solo el contenido parcial
        return render(request, 'productos/partials/lista_notificaciones.html', context)
    
    return render(request, 'productos/notificaciones.html', context)

@login_required
def marcar_notificacion_leida(request, pk):
    """Vista para marcar una notificación como leída"""
    notificacion = get_object_or_404(StockNotification, pk=pk)
    notificacion.marcar_como_leida(request.user)
    
    if request.headers.get('HX-Request'):
        return HttpResponse('')
    
    return redirect('productos:lista_notificaciones')

@login_required
def notificaciones_no_leidas(request):
    """API para obtener el conteo y lista de notificaciones no leídas"""
    notificaciones = StockNotification.objects.filter(
        destinatarios=request.user
    ).select_related('producto')[:5]
    
    html = render_to_string('productos/partials/notificaciones_dropdown.html', {
        'notificaciones': notificaciones
    }, request=request)
    
    return JsonResponse({
        'count': notificaciones.count(),
        'html': html
    })

@login_required
def notificaciones_stock(request):
    """Vista básica para notificaciones de stock"""
    # Obtener productos con stock bajo
    productos_stock_bajo = Producto.objects.filter(
        activo=True,
        cantidad__lte=models.F('cantidad_minima')
    ).select_related('categoria')
    
    # Obtener productos agotados
    productos_agotados = Producto.objects.filter(
        activo=True,
        cantidad=0
    ).select_related('categoria')
    
    notifications = []
    
    # Agregar notificaciones de productos agotados
    for producto in productos_agotados:
        notifications.append({
            'id': f'agotado_{producto.id}',
            'tipo': 'agotado',
            'mensaje': f'¡URGENTE! El producto {producto.nombre} se ha agotado.',
            'producto': producto.nombre,
            'prioridad': 'critica',
            'fecha': producto.fecha_actualizacion.isoformat() if producto.fecha_actualizacion else None
        })
    
    # Agregar notificaciones de stock bajo
    for producto in productos_stock_bajo:
        if producto.cantidad > 0:  # No incluir los ya agotados
            notifications.append({
                'id': f'stock_bajo_{producto.id}',
                'tipo': 'stock_bajo',
                'mensaje': f'Stock bajo: {producto.nombre} (Cantidad: {producto.cantidad}, Mínimo: {producto.cantidad_minima})',
                'producto': producto.nombre,
                'prioridad': 'alta' if producto.cantidad <= (producto.cantidad_minima * 0.5) else 'media',
                'fecha': producto.fecha_actualizacion.isoformat() if producto.fecha_actualizacion else None
            })
    
    return JsonResponse({
        'status': 'ok', 
        'notifications': notifications,
        'count': len(notifications)
    })

@login_required
def marcar_notificacion_leida(request, pk):
    """Marcar una notificación como leída"""
    if request.method == 'POST':
        # En una implementación completa, aquí guardaríamos el estado en la base de datos
        return JsonResponse({'status': 'ok', 'message': 'Notificación marcada como leída'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})

@login_required
def panel_notificaciones(request):
    """Vista para mostrar el panel de notificaciones"""
    productos_stock_bajo = Producto.objects.filter(
        activo=True,
        cantidad__lte=models.F('cantidad_minima')
    ).select_related('categoria')
    
    productos_agotados = productos_stock_bajo.filter(cantidad=0)
    productos_criticos = productos_stock_bajo.filter(
        cantidad__gt=0,
        cantidad__lte=models.F('cantidad_minima') * 0.5
    )
    productos_advertencia = productos_stock_bajo.filter(
        cantidad__gt=models.F('cantidad_minima') * 0.5
    )
    
    context = {
        'productos_agotados': productos_agotados,
        'productos_criticos': productos_criticos,
        'productos_advertencia': productos_advertencia,
        'total_notificaciones': productos_stock_bajo.count(),
    }
    
    return render(request, 'productos/notificaciones.html', context)

@login_required
def resumen_stock(request):
    """Vista AJAX para obtener resumen de stock"""
    from django.db.models import Count, Q
    
    resumen = {
        'total_productos': Producto.objects.filter(activo=True).count(),
        'productos_agotados': Producto.objects.filter(activo=True, cantidad=0).count(),
        'productos_stock_bajo': Producto.objects.filter(
            activo=True,
            cantidad__lte=models.F('cantidad_minima'),
            cantidad__gt=0
        ).count(),
        'productos_ok': Producto.objects.filter(
            activo=True,
            cantidad__gt=models.F('cantidad_minima')
        ).count(),
    }
    
    return JsonResponse(resumen)