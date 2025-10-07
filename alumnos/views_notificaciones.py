from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator

from .models_notificaciones import Notificacion

@login_required
def lista_notificaciones(request):
    """Vista para listar todas las notificaciones del usuario"""
    # Obtener notificaciones del usuario
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    
    # Filtrar por tipo si se especifica
    tipo = request.GET.get('tipo')
    if tipo:
        notificaciones = notificaciones.filter(tipo=tipo)
    
    # Filtrar por estado de lectura
    estado = request.GET.get('estado')
    if estado == 'no_leidas':
        notificaciones = notificaciones.filter(leida=False)
    elif estado == 'leidas':
        notificaciones = notificaciones.filter(leida=True)
    
    # Paginación
    paginator = Paginator(notificaciones, 20)  # 20 notificaciones por página
    page = request.GET.get('page')
    notificaciones_paginadas = paginator.get_page(page)
    
    context = {
        'notificaciones': notificaciones_paginadas,
        'tipo_actual': tipo,
        'estado_actual': estado,
        'total_no_leidas': Notificacion.objects.filter(usuario=request.user, leida=False).count()
    }
    
    return render(request, 'alumnos/notificaciones/lista.html', context)

@login_required
def detalle_notificacion(request, notificacion_id):
    """Vista para ver el detalle de una notificación"""
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    
    # Marcar como leída si no lo está
    if not notificacion.leida:
        notificacion.marcar_como_leida()
    
    # Si hay una URL de acción, redirigir
    if notificacion.url_accion:
        return redirect(notificacion.url_accion)
    
    return render(request, 'alumnos/notificaciones/detalle.html', {
        'notificacion': notificacion
    })

@login_required
def marcar_leida(request, notificacion_id):
    """Vista para marcar una notificación como leída vía AJAX"""
    try:
        notificacion = Notificacion.objects.get(id=notificacion_id, usuario=request.user)
        notificacion.marcar_como_leida()
        return JsonResponse({'success': True})
    except Notificacion.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

@login_required
def marcar_todas_leidas(request):
    """Vista para marcar todas las notificaciones como leídas"""
    Notificacion.objects.filter(
        usuario=request.user, 
        leida=False
    ).update(
        leida=True, 
        fecha_lectura=timezone.now()
    )
    
    return JsonResponse({'success': True})

@login_required
def eliminar_notificacion(request, notificacion_id):
    """Vista para eliminar una notificación"""
    try:
        notificacion = Notificacion.objects.get(id=notificacion_id, usuario=request.user)
        notificacion.delete()
        return JsonResponse({'success': True})
    except Notificacion.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

@login_required
def eliminar_leidas(request):
    """Vista para eliminar todas las notificaciones leídas"""
    Notificacion.objects.filter(
        usuario=request.user, 
        leida=True
    ).delete()
    
    return JsonResponse({'success': True})

@login_required
def contador_no_leidas(request):
    """Vista para obtener el contador de notificaciones no leídas vía AJAX"""
    count = Notificacion.objects.filter(
        usuario=request.user, 
        leida=False
    ).count()
    
    return JsonResponse({'count': count})