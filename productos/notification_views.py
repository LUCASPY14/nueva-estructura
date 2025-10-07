from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from .notifications import StockNotification

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