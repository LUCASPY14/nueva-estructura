from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from .forms import LoginForm, RegistroPadreForm, UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()

# Página pública
def landing(request):
    return render(request, 'usuarios/landing.html')

# Helpers de rol
def es_admin(user):
    return user.is_superuser or (hasattr(user, 'tipo') and user.tipo == 'ADMIN')

def es_cajero(user):
    return user.groups.filter(name='Cajeros').exists() or (hasattr(user, 'tipo') and user.tipo == 'CAJERO')

def es_padre(user):
    return hasattr(user, 'padre_profile') or (hasattr(user, 'tipo') and user.tipo == 'PADRE')

# Función centralizada para redirigir por tipo de usuario
def redirigir_por_tipo(user):
    if user.tipo == 'ADMIN':
        return redirect('usuarios:dashboard_admin')
    elif user.tipo == 'CAJERO':
        return redirect('usuarios:dashboard_cajero')
    elif user.tipo == 'PADRE':
        return redirect('usuarios:dashboard_padre')
    return redirect('usuarios:landing')

# Login visual
def login_simple(request):
    if request.user.is_authenticated:
        return redirigir_por_tipo(request.user)

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirigir_por_tipo(user)
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

# Logout
def logout_view(request):
    logout(request)
    return redirect('usuarios:landing')

# Registro de padres
def registro_padre(request):
    if request.method == 'POST':
        form = RegistroPadreForm(request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth.models import Group
            padres_group, _ = Group.objects.get_or_create(name="Padres")
            user.groups.add(padres_group)
            login(request, user)
            return redirect('usuarios:dashboard_padre')
    else:
        form = RegistroPadreForm()
    return render(request, 'usuarios/registro_padre.html', {'form': form})

# Dashboards por rol
@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def dashboard_admin(request):
    items = [
        {
            'title': 'Gestión de Usuarios',
            'description': 'Agregar, editar o eliminar usuarios del sistema.',
            'icon': '👥',
            'url': reverse('usuarios:usuarios_lista')
        },
        {
            'title': 'Productos',
            'description': 'Controlar y administrar los productos disponibles.',
            'icon': '🍔',
            'url': reverse('productos:listar_productos')
        },
        {
            'title': 'Reportes de Ventas',
            'description': 'Ver estadísticas y descargar reportes de ventas.',
            'icon': '💰',
            'url': reverse('ventas:reporte_ventas')
        },
        {
            'title': 'Stock',
            'description': 'Ver el estado actual del inventario.',
            'icon': '📦',
            'url': reverse('reportes:reporte_stock')
        },
        {
            'title': 'Facturación',
            'description': 'Revisar facturas generadas en el sistema.',
            'icon': '🧾',
            'url': reverse('facturacion:reporte_facturas')
        },
        {
            'title': 'Configuración del Sistema',
            'description': 'Editar parámetros globales del sistema LGservice.',
            'icon': '⚙️',
            'url': reverse('configuracion:configuracion')
        },
    ]
    return render(request, 'usuarios/dashboard_admin.html', {'items': items})


@login_required
@user_passes_test(es_cajero, login_url='usuarios:login_simple')
def dashboard_cajero(request):
    return render(request, 'usuarios/dashboard_cajero.html')

@login_required
@user_passes_test(es_padre, login_url='usuarios:login_simple')
def dashboard_padre(request):
    from alumnos.models import Alumno
    try:
        alumnos = request.user.padre_profile.alumnos.all()
    except Exception:
        alumnos = []
    return render(request, 'usuarios/dashboard_padre.html', {'alumnos': alumnos})

# Gestión de usuarios (solo admin)
@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def usuarios_lista(request):
    usuarios = User.objects.all().order_by('username')
    return render(request, 'usuarios/usuarios_lista.html', {'usuarios': usuarios})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def usuario_crear(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('usuarios:usuarios_lista')
    else:
        form = UserCreationForm()
    return render(request, 'usuarios/usuario_form.html', {'form': form, 'crear': True})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('usuarios:usuarios_lista')
    else:
        form = UserChangeForm(instance=usuario)
    return render(request, 'usuarios/usuario_form.html', {'form': form, 'crear': False})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def usuario_eliminar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado exitosamente.')
        return redirect('usuarios:usuarios_lista')
    return render(request, 'usuarios/usuario_confirmar_eliminar.html', {'usuario': usuario})

# Dashboards alternativos (si se usan)
@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def admin_dashboard_view(request):
    return render(request, 'dashboard/admin_dashboard.html')

@login_required
@user_passes_test(es_padre, login_url='usuarios:login_simple')
def padre_dashboard_view(request):
    return render(request, 'dashboard/padre_dashboard.html')

@login_required
@user_passes_test(es_cajero, login_url='usuarios:login_simple')
def cajero_dashboard_view(request):
    return render(request, 'dashboard/cajero_dashboard.html')
