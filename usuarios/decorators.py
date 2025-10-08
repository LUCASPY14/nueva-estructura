from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def role_required(roles):
    """
    Decorador que verifica si el usuario tiene uno de los roles especificados
    
    Args:
        roles: Lista de roles permitidos ['administrador', 'cajero', 'padre', 'supervisor']
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'tipo_usuario'):
                messages.error(request, 'Su usuario no tiene un tipo asignado. Contacte al administrador.')
                return redirect('core:home')
            
            if request.user.tipo_usuario not in roles:
                messages.error(request, 'No tiene permisos para acceder a esta sección.')
                return redirect('core:home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """Decorador para vistas que requieren permisos de administrador"""
    return role_required(['administrador'])(view_func)

def cajero_required(view_func):
    """Decorador para vistas que requieren permisos de cajero"""
    return role_required(['administrador', 'cajero'])(view_func)

def padre_required(view_func):
    """Decorador para vistas que requieren permisos de padre"""
    return role_required(['padre'])(view_func)

def supervisor_required(view_func):
    """Decorador para vistas que requieren permisos de supervisor"""
    return role_required(['administrador', 'supervisor'])(view_func)

def admin_or_cajero_required(view_func):
    """Decorador para vistas que requieren permisos de administrador o cajero"""
    return role_required(['administrador', 'cajero'])(view_func)

def admin_or_supervisor_required(view_func):
    """Decorador para vistas que requieren permisos de administrador o supervisor"""
    return role_required(['administrador', 'supervisor'])(view_func)