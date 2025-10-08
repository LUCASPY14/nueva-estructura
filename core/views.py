from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone

def home(request):
    """Vista principal del sistema"""
    context = {
        'title': 'LGService - Sistema de Gestión Escolar',
        'user': request.user,
    }
    
    # Si el usuario está autenticado, agregar estadísticas
    if request.user.is_authenticated:
        try:
            # Importar modelos dinámicamente para evitar errores circulares
            from django.apps import apps
            
            # Obtener modelos si existen
            try:
                Alumno = apps.get_model('alumnos', 'Alumno')
                context['total_alumnos'] = Alumno.objects.count()
            except:
                context['total_alumnos'] = 0
            
            try:
                Producto = apps.get_model('productos', 'Producto')
                context['total_productos'] = Producto.objects.filter(activo=True).count()
            except:
                context['total_productos'] = 0
            
            try:
                Venta = apps.get_model('ventas', 'Venta')
                context['ventas_hoy'] = Venta.objects.filter(
                    fecha_venta__date=timezone.now().date()
                ).count()
                context['ingresos_mes'] = Venta.objects.filter(
                    fecha_venta__month=timezone.now().month,
                    fecha_venta__year=timezone.now().year
                ).aggregate(total=Sum('total'))['total'] or 0
            except:
                context['ventas_hoy'] = 0
                context['ingresos_mes'] = 0
                
        except Exception as e:
            pass
    
    return render(request, 'core/home.html', context)

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
