from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from .models import TurnoCajero

def require_active_turno(view_func):
    """Decorador que requiere un turno activo"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Autenticación requerida'}, status=401)
        
        turno_activo = TurnoCajero.objects.filter(
            cajero=request.user,
            activa=True,
            fecha_fin__isnull=True
        ).exists()
        
        if not turno_activo:
            if request.headers.get('content-type') == 'application/json':
                return JsonResponse({'error': 'No tienes un turno activo'}, status=400)
            else:
                messages.warning(request, 'Debes abrir un turno antes de continuar.')
                return redirect('ventas:abrir_turno')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def cajero_required(view_func):
    """Decorador que requiere permisos de cajero"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Autenticación requerida'}, status=401)
        
        if not (request.user.is_staff or request.user.is_superuser):
            if request.headers.get('content-type') == 'application/json':
                return JsonResponse({'error': 'Permisos insuficientes'}, status=403)
            else:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view