from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from usuarios.decorators import admin_or_supervisor_required
from .models import ConfiguracionSistema
from .forms import ConfiguracionForm

@login_required
@admin_or_supervisor_required
def configuracion_general(request):
    return render(request, 'configuracion/general.html', {'title': 'Configuración General'})

@login_required
@admin_or_supervisor_required
def configuracion_sistema(request):
    return render(request, 'configuracion/sistema.html', {'title': 'Configuración del Sistema'})

@login_required
@admin_or_supervisor_required
def configuracion_notificaciones(request):
    return render(request, 'configuracion/notificaciones.html', {'title': 'Configuración de Notificaciones'})

@login_required
@admin_or_supervisor_required
def backup_sistema(request):
    return render(request, 'configuracion/backup.html', {'title': 'Backup del Sistema'})

@login_required
@admin_or_supervisor_required
def configuracion_usuarios(request):
    return render(request, 'configuracion/usuarios.html', {'title': 'Configuración de Usuarios'})

def configuracion_view(request):
    config, _ = ConfiguracionSistema.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return redirect('configuracion:editar_configuracion')
    else:
        form = ConfiguracionForm(instance=config)

    return render(request, 'configuracion/configuracion.html', {'form': form})