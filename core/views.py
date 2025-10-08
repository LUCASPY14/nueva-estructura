from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import date

def home(request):
    """Vista principal del sistema - Cantina de Tita"""
    context = {
        'title': 'Cantina de Tita - Sistema de Gestión',
        'user': request.user,
    }
    
    # Agregar estadísticas del sistema
    try:
        # Importar modelos dinámicamente para evitar errores circulares
        from django.apps import apps
        
        # Estadísticas de Alumnos
        try:
            Alumno = apps.get_model('alumnos', 'Alumno')
            context['total_alumnos'] = Alumno.objects.filter(activo=True).count()
            # Calcular saldo total de todos los alumnos
            context['saldo_total'] = Alumno.objects.aggregate(
                total=Sum('saldo_tarjeta')
            )['total'] or 0
        except:
            context['total_alumnos'] = 0
            context['saldo_total'] = 0
        
        # Estadísticas de Productos
        try:
            Producto = apps.get_model('productos', 'Producto')
            context['productos_activos'] = Producto.objects.filter(activo=True).count()
        except:
            context['productos_activos'] = 0
        
        # Estadísticas de Ventas (solo del día actual)
        try:
            Venta = apps.get_model('ventas', 'Venta')
            hoy = timezone.now().date()
            ventas_hoy = Venta.objects.filter(fecha__date=hoy)
            context['ventas_hoy'] = ventas_hoy.count()
            context['total_recaudado'] = ventas_hoy.aggregate(
                total=Sum('total')
            )['total'] or 0
        except:
            context['ventas_hoy'] = 0
            context['total_recaudado'] = 0
        try:
            Producto = apps.get_model('productos', 'Producto')
            context['total_productos'] = Producto.objects.filter(activo=True).count()
        except:
            context['total_productos'] = 0
        
        # Ventas del día (placeholder por ahora)
        context['ventas_hoy'] = 0  # TODO: implementar cuando esté el módulo de ventas
        
    except Exception as e:
        # En caso de error, usar valores por defecto
        context.update({
            'total_alumnos': 0,
            'saldo_total': 0,
            'productos_activos': 0,
            'ventas_hoy': 0,
            'total_recaudado': 0
        })
    
    return render(request, 'home_cantina.html', context)

@login_required
def dashboard(request):
    """Dashboard principal según el tipo de usuario"""
    user = request.user
    
    # Redirigir según el tipo de usuario
    if user.groups.filter(name='Administradores').exists() or user.is_superuser:
        return render(request, 'core/dashboard_admin.html', {
            'title': 'Panel de Administración'
        })
    elif user.groups.filter(name='Cajeros').exists():
        return render(request, 'core/dashboard_cajero.html', {
            'title': 'Panel de Cajero'
        })
    elif user.groups.filter(name='Padres').exists():
        return render(request, 'core/dashboard_padre.html', {
            'title': 'Panel de Padre'
        })
    else:
        return render(request, 'core/dashboard_general.html', {
            'title': 'Panel de Usuario'
        })
