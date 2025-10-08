from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from usuarios.decorators import admin_or_supervisor_required
from django.http import HttpResponse

@login_required
@admin_or_supervisor_required
def dashboard_reportes(request):
    return render(request, 'reportes/dashboard.html', {'title': 'Dashboard de Reportes'})

@login_required
@admin_or_supervisor_required
def reporte_ventas(request):
    return render(request, 'reportes/ventas.html', {'title': 'Reporte de Ventas'})

@login_required
@admin_or_supervisor_required
def reporte_productos(request):
    return render(request, 'reportes/productos.html', {'title': 'Reporte de Productos'})

@login_required
@admin_or_supervisor_required
def reporte_alumnos(request):
    return render(request, 'reportes/alumnos.html', {'title': 'Reporte de Alumnos'})

@login_required
@admin_or_supervisor_required
def reporte_financiero(request):
    return render(request, 'reportes/financiero.html', {'title': 'Reporte Financiero'})

@login_required
@admin_or_supervisor_required
def exportar_reporte(request, tipo):
    # Vista para exportar reportes en diferentes formatos
    return HttpResponse(f"Exportando reporte: {tipo}", content_type="text/plain")
