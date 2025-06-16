from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponseForbidden
from .models import Padre, Alumno, Restriccion
from .forms import AlumnoForm, PadreForm, CargarSaldoForm, RestriccionForm

def es_admin(user):
    return user.is_superuser or user.groups.filter(name='Administradores').exists()

def es_padre(user):
    return hasattr(user, 'padre_profile')

# --- ADMINISTRADOR ---

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def alumnos_lista(request):
    alumnos = Alumno.objects.select_related('padre').all()
    return render(request, 'alumnos/alumnos_lista.html', {'alumnos': alumnos})

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def crear_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Alumno creado correctamente.")
            return redirect('alumnos:alumnos_lista')
    else:
        form = AlumnoForm()
    return render(request, 'alumnos/alumno_form.html', {'form': form})

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def editar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, "Alumno actualizado correctamente.")
            return redirect('alumnos:alumnos_lista')
    else:
        form = AlumnoForm(instance=alumno)
    return render(request, 'alumnos/alumno_form.html', {'form': form})

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def eliminar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    if request.method == 'POST':
        alumno.delete()
        messages.success(request, "Alumno eliminado correctamente.")
        return redirect('alumnos:alumnos_lista')
    return render(request, 'alumnos/alumno_confirm_delete.html', {'alumno': alumno})

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def listar_restricciones(request):
    restricciones = Restriccion.objects.select_related('alumno', 'producto').all()
    return render(request, 'alumnos/restricciones_lista.html', {'restricciones': restricciones})

# --- PADRE ---

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_padre, login_url='usuarios:login_simple')
def mis_hijos(request):
    hijos = request.user.padre_profile.alumnos.all()
    return render(request, 'alumnos/mis_hijos.html', {'hijos': hijos})

@login_required(login_url='usuarios:login_simple')
def detalle_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    if es_admin(request.user) or (es_padre(request.user) and alumno.padre.usuario == request.user):
        return render(request, 'alumnos/detalle_alumno.html', {'alumno': alumno})
    else:
        messages.error(request, "No tienes permiso para ver este alumno.")
        return redirect('alumnos:mis_hijos')

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_admin, login_url='usuarios:login_simple')
@transaction.atomic
def cargar_saldo(request):
    if request.method == 'POST':
        form = CargarSaldoForm(request.POST)
        if form.is_valid():
            alumno = form.cleaned_data['alumno']
            monto = form.cleaned_data['monto']
            if monto <= 0:
                messages.error(request, "El monto debe ser mayor a cero.")
            else:
                alumno.saldo_tarjeta += monto
                alumno.save()
                messages.success(request, f"Saldo cargado correctamente a {alumno.nombre}.")
                return redirect('alumnos:alumnos_lista')
    else:
        form = CargarSaldoForm()
    return render(request, 'alumnos/cargar_saldo.html', {'form': form})

@login_required(login_url='usuarios:login_simple')
@user_passes_test(es_padre, login_url='usuarios:login_simple')
def editar_perfil_padre(request):
    padre = request.user.padre_profile
    if request.method == 'POST':
        form = PadreForm(request.POST, instance=padre)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('alumnos:mis_hijos')
    else:
        form = PadreForm(instance=padre)
    return render(request, 'alumnos/editar_perfil_padre.html', {'form': form})

# --- RESTRICCIONES ---

@login_required(login_url='usuarios:login_simple')
def crear_restriccion(request):
    if not (es_admin(request.user) or es_padre(request.user)):
        messages.error(request, "No tienes permiso para crear restricciones.")
        return redirect('alumnos:mis_hijos')
    if request.method == 'POST':
        form = RestriccionForm(request.POST)
        if form.is_valid():
            restriccion = form.save(commit=False)
            if es_padre(request.user) and restriccion.alumno.padre.usuario != request.user:
                messages.error(request, "Solo puedes crear restricciones para tus hijos.")
                return redirect('alumnos:mis_hijos')
            restriccion.save()
            messages.success(request, "Restricción creada correctamente.")
            return redirect('alumnos:listar_restricciones')
    else:
        form = RestriccionForm()
    return render(request, 'alumnos/restriccion_form.html', {'form': form})

@login_required(login_url='usuarios:login_simple')
def eliminar_restriccion(request, pk):
    restriccion = get_object_or_404(Restriccion, pk=pk)
    user = request.user
    puede_eliminar = es_admin(user) or (es_padre(user) and restriccion.alumno.padre.usuario == user)

    if not puede_eliminar:
        return HttpResponseForbidden("No tienes permiso para eliminar esta restricción.")

    if request.method == 'POST':
        restriccion.delete()
        messages.success(request, "Restricción eliminada correctamente.")
        return redirect('alumnos:listar_restricciones')

    return render(request, 'alumnos/restriccion_confirm_delete.html', {'restriccion': restriccion})
