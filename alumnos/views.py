from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from usuarios.decorators import admin_required, admin_or_cajero_required, padre_required
from .models import Alumno

@login_required
@admin_or_cajero_required
def lista_alumnos(request):
    alumnos = Alumno.objects.all()
    return render(request, 'alumnos/lista.html', {
        'title': 'Lista de Alumnos',
        'alumnos': alumnos
    })

@login_required
@admin_required
def crear_alumno(request):
    # Vista placeholder - implementar lógica de creación
    return render(request, 'alumnos/crear.html', {'title': 'Crear Alumno'})

@login_required
@admin_required
def editar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    return render(request, 'alumnos/editar.html', {
        'title': 'Editar Alumno',
        'alumno': alumno
    })

@login_required
def ver_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    return render(request, 'alumnos/ver.html', {
        'title': 'Ver Alumno',
        'alumno': alumno
    })

@login_required
def consultar_saldo(request):
    # Vista para padres o administradores consultar saldo
    if request.user.es_padre:
        # Mostrar solo los hijos del padre
        alumnos = Alumno.objects.filter(padre=request.user)
    else:
        # Administradores pueden ver todos
        alumnos = Alumno.objects.all()
    
    return render(request, 'alumnos/saldo.html', {
        'title': 'Consultar Saldo',
        'alumnos': alumnos
    })

@login_required
def historial_movimientos(request):
    # Vista para ver historial de movimientos
    if request.user.es_padre:
        alumnos = Alumno.objects.filter(padre=request.user)
    else:
        alumnos = Alumno.objects.all()
    
    return render(request, 'alumnos/historial.html', {
        'title': 'Historial de Movimientos',
        'alumnos': alumnos
    })
