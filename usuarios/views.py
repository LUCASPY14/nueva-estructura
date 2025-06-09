from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from .forms import LoginForm, RegistroPadreForm, AuthenticationForm

# Página pública
def landing(request):
    return render(request, 'usuarios/landing.html')


# Verifica si el usuario pertenece al grupo 'Cajeros'
def es_cajero(user):
    return user.groups.filter(name='Cajeros').exists()


# Login
def login_simple(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('usuarios:dashboard_admin')
            elif hasattr(user, 'padre'):
                return redirect('usuarios:dashboard_padre')
            elif user.groups.filter(name='Cajeros').exists():
                return redirect('usuarios:dashboard_cajero')
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})


# Logout
def logout_view(request):
    logout(request)
    return redirect('usuarios:landing')


# Registro padres
def registro_padre(request):
    if request.method == 'POST':
        form = RegistroPadreForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('usuarios:dashboard_padre')
    else:
        form = RegistroPadreForm()
    return render(request, 'usuarios/registro_padre.html', {'form': form})


# Dashboards por rol
@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard_view(request):
    return render(request, 'dashboard/admin_dashboard.html')

@login_required
@user_passes_test(lambda u: hasattr(u, 'padre'))
def padre_dashboard_view(request):
    return render(request, 'dashboard/padre_dashboard.html')

@login_required
@user_passes_test(es_cajero)
def cajero_dashboard_view(request):
    return render(request, 'dashboard/cajero_dashboard.html')


# Dashboards alternativos (templates en usuarios/)
@login_required
def dashboard_admin(request):
    return render(request, 'usuarios/dashboard_admin.html')

@login_required
def dashboard_cajero(request):
    return render(request, 'usuarios/dashboard_cajero.html')

@login_required
def dashboard_padre(request):
    from alumnos.models import Alumno
    alumnos = request.user.padre_profile.alumnos.all()
    return render(request, 'usuarios/dashboard_padre.html', {'alumnos': alumnos})
