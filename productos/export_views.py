# productos/export_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages

@login_required
def exportar_productos(request):
    """Vista básica para exportar productos"""
    messages.info(request, "Funcionalidad de exportación en desarrollo")
    return HttpResponse("Exportación en desarrollo", content_type="text/plain")

@login_required
def exportar_stock(request):
    """Exportar reporte de stock"""
    messages.info(request, "Funcionalidad de exportación en desarrollo")
    return HttpResponse("Exportación de stock en desarrollo", content_type="text/plain")