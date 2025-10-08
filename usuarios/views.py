from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from .forms import LoginForm, RegistroPadreForm, CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.views import LoginView
from usuarios.models import CustomUser
from ventas.models import Venta
from productos.models import Producto
from compras.models import Compra  # Asegúrate que solo importa Compra, no Proveedor


User = get_user_model()

# Página pública
def landing(request):
    return render(request, 'usuarios/landing.html')

# Helpers de rol
def es_admin(user):
    """Verifica si el usuario es administrador"""
    return user.is_superuser or user.groups.filter(name='Administradores').exists()

def es_cajero(user):
    return user.groups.filter(name='Cajeros').exists() or (hasattr(user, 'tipo') and user.tipo == 'CAJERO')

def es_padre(user):
    return hasattr(user, 'padre_profile') or (hasattr(user, 'tipo') and user.tipo == 'PADRE')

def es_admin_o_cajero(user):
    """Verifica si el usuario es administrador o cajero"""
    return user.is_superuser or user.groups.filter(name__in=['Administradores', 'Cajeros']).exists()

# Función centralizada para redirigir por tipo de usuario
def redirigir_por_tipo(user):
    if user.tipo == 'ADMIN':
        return reverse('usuarios:dashboard_admin')
    elif user.tipo == 'CAJERO':
        return reverse('usuarios:dashboard_cajero')
    elif user.tipo == 'PADRE':
        return reverse('usuarios:dashboard_padre')
    return reverse('usuarios:landing')

# Login visual
class LoginSimpleView(LoginView):
    template_name = 'registration/login.html'  # Usa el template existente
    authentication_form = LoginForm

    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contraseña incorrectos.")
        return redirect('usuarios:login_simple')

    def get_success_url(self):
        return redirigir_por_tipo(self.request.user)

def logout_view(request):
    logout(request)
    return redirect('usuarios:landing')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'usuarios/login.html')

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
    total_usuarios = CustomUser.objects.count()
    total_admins = CustomUser.objects.filter(tipo_usuario='administrador').count()
    total_cajeros = CustomUser.objects.filter(tipo_usuario='cajero').count()
    total_padres = CustomUser.objects.filter(tipo_usuario='padre').count()
    ventas_recientes = Venta.objects.order_by('-fecha')[:5]
    productos_bajo_stock = Producto.objects.filter(cantidad__lte=10).order_by('cantidad')[:5]  # Ajusta el número y el umbral según tu lógica
    compras_recientes = Compra.objects.order_by('-fecha')[:5]

    context = {
        'total_usuarios': total_usuarios,
        'total_admins': total_admins,
        'total_cajeros': total_cajeros,
        'total_padres': total_padres,
        'ventas_recientes': ventas_recientes,
        'productos_bajo_stock': productos_bajo_stock,
        'compras_recientes': compras_recientes,
    }
    return render(request, 'usuarios/dashboard_admin.html', context)


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
    usuarios = CustomUser.objects.all()
    return render(request, 'usuarios/usuarios_lista.html', {'usuarios': usuarios})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def usuario_crear(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('usuarios:usuarios_lista')
    else:
        form = CustomUserCreationForm()
    return render(request, 'usuarios/usuario_form.html', {'form': form, 'crear': True})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('usuarios:usuarios_lista')
    else:
        form = CustomUserChangeForm(instance=usuario)
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

@login_required
def perfil_view(request):
    return render(request, 'usuarios/perfil.html')


